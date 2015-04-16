#!/bin/bash

DUSEGD=/d/sw/dusegd/latest/dusegd

die () {
    echo "$@" >&2
    exit 1
}

usage () {
    echo
    echo "Usage:  $0 tape=/dev/dst# disk=/path/to/segd/line [optional parameters]"
    echo
    echo '  Required parameters:'
    echo '    tape= a device of the format /dev/dst#'
    echo
    echo '    disk= the directory from which to read .FFID files'
    echo
    echo
    echo '  Optional parameters:'
    echo '    firsttape= first tape record; defaults to record #1'
    echo '               Normally not used, but can be used to restart a QC from mid-tape.'
    echo
    echo '    firstdisk= first disk record; defaults to the first file in the disk= directory'
    echo '               Set this for tapes 2-n of a multi-reel sequence.'
    echo
    echo '    lastdisk= last disk record; defaults to the last file in the disk= directory'
    echo '              Set this for all but the last tape of a multi-reel sequence.'
    echo
    echo '    log= write a copy of all output into this file'
    echo
    exit 100
}

firstFFID=
lastFFID=
logfile=

output () {
    if [[ -n "$logfile" ]]; then
        awk '{printf("%s    %s\n",strftime(),$0); fflush()}' | tee "$logfile"
    else
        awk '{printf("%s    %s\n",strftime(),$0); fflush()}'
    fi
}

# Some sanity checks
[[ $# -lt 1 ]] && usage
	
# Process arguments
true
while [[ $? -eq 0 ]]; do
    cmd=${1%%=*}
    arg=${1#${cmd}=}
    case "$cmd" in
	'tape') tape=$arg ;;
        'disk') disk=$arg ;;
        'firsttape') taperecord=$((10#$arg)) ;; # force base-10
        'firstdisk') firstFFID=$((10#$arg)) ;; # force base-10
        'lastdisk') lastFFID=$((10#$arg)) ;; # force base-10
        'log') logfile=$arg ;;
	'') ;;
	*) die "Unknown command line argument: $cmd" ;;
    esac
    
    shift
done


[[ ! $disk ]] && usage
[[ ! -d $disk ]] && die "$disk is not a directory."

#check tape specified and of format /dev/dst[0-9]*
[[ ! $tape ]] && usage

[[ ! -z ${tape##\/dev\/dst[0-9]*} ]] && die "tape= should be of the format /dev/dst#"

# check ffid and taperecord are ints
[[ ! -z ${firstFFID##[0-9]*} ]] && die "If provided, firstdisk= must be an integer."
[[ ! -z ${lastFFID##[0-9]*} ]] && die "If provided, lastdisk= must be an integer."
[[ ! -z ${taperecord##[0-9]*} ]] && die "If provided, firsttape= must be an integer."

md5() {
    md5sum | cut -d ' ' -f 1
}

getNextTapeChkSum() {
    tapeMd5sum=$(dd if="$1" bs=1024k 2>/dev/null | $DUSEGD input_file=- output_file=- 2>/dev/null | md5)
}

getCurrentRecord() {
    currentrecord=$(mt -f $tape status | grep -o "File number=[0-9]*" | cut -d '=' -f 2)
    # mt counts from 0; humans count from 1
    currentrecord=$((currentrecord + 1))
}

checkDiskFileID() {
    if [[ $ffid -le $lastFile ]]; then
        return
    fi

    if [[ -n "$lastFFID" ]]; then
        echo "Tape contains more records, but we've reached the specified lastdisk=$lastFFID"
    else
        echo Tape contains more records, but there are no more files in the disk directory.
    fi
    echo TAPE QC UNSUCCESSFUL -- exiting without rewinding or ejecting
    exit 100
}

begintime=$(date +%s)
{
    echo Checking tape
    until mt -f $tape status >/dev/null 2>&1; do
	sleep 5
    done

    getCurrentRecord
    if [[ $taperecord ]]; then
	echo "Forwarding tape to record $taperecord"
        # humans count from 1; mt counts from 0
	mt -f $tape asf $((taperecord - 1))
        currentrecord=$taperecord
    
    elif [[ ! $currentrecord == 1 ]]; then
 	echo "Tape is currently at record $currentrecord"
	echo "Rewind tape? [y/n]  "
        read -a confirmRewind

        if [[ $confirmRewind == [yY] ]]; then 
		echo Rewinding tape
		mt -f $tape rewind
                getCurrentRecord
	fi
    fi

    cd "$disk"

    if [[ -n "$firstFFID" ]]; then
        ffid=$firstFFID
    else
        ffid=$(ls -1 | grep -w "[0-9]*.ffid" | cut -d '.' -f 1 | sort | head -1 | sed 's/^0*//')
        firstFFID=$ffid
    fi
    if [[ -n "$lastFFID" ]]; then
        lastFile=$lastFFID
    else
        lastFile=$(ls -1 | grep -w "[0-9]*.ffid" | cut -d '.' -f 1 | sort | tail -1 | sed 's/^0*//')
    fi

    missing=0

    echo "Reading disk files from $disk"
    echo Starting at ffid: $ffid
    echo Starting at tape record: $currentrecord

    while getNextTapeChkSum "$tape"; do
        if [[ "$tapeMd5sum" == "d41d8cd98f00b204e9800998ecf8427e" ]]; then
            break # This is the magic "empty record" checksum
        fi

	readFile=$(printf "%08d.ffid" $ffid)
	while [[ ! -s $readFile ]]; do
		checkDiskFileID
		echo "File $readFile not found.  Continuing to next disk file."
                missing=$((missing+1))
		ffid=$((ffid+1))
		readFile=$(printf "%08d.ffid" $ffid)
	done

        checkDiskFileID
	sourceMd5sum=$($DUSEGD input_file=$readFile output_file=- 2>/dev/null | md5)

	if [[ $sourceMd5sum == $tapeMd5sum ]]; then
		echo "OK -- disk file $readFile ($sourceMd5sum) matches tape record $currentrecord ($tapeMd5sum)"
	else
		echo "Disk file $readFile ($sourceMd5sum) doesn't match tape record $currentrecord ($tapeMd5sum)"
                echo TAPE QC UNSUCCESSFUL -- exiting without rewinding or ejecting
		exit 100
	fi

        currentrecord=$((currentrecord+1))
	ffid=$((ffid+1))
    done
    echo "End of tape."

    if [[ -n "$lastFFID" ]]; then
        # We should expect ffid to be lastFFID+1 (if provided) after a successful tape read.
        if [[ $ffid -ne $((lastFFID + 1)) ]]; then
            echo "I've reached the end of the tape, and the last file I QC'd was $((ffid-1)) -- but you said lastdisk=$lastFFID"
            echo TAPE QC UNSUCCESSFUL -- exiting without rewinding or ejecting
            exit 100
        fi
    else
        # Otherwise ffid should be one past the last file, i.e. not exist
        if [[ -s $(printf "%08d.ffid" $ffid) ]]; then
            echo "I've reached the end of the tape, but there are more files in the disk directory!"
            echo TAPE QC UNSUCCESSFUL -- exiting without rewinding or ejecting
            exit 100
        fi
    fi

    echo -----
    echo "Tape QC successful: $disk"
    echo "First FFID   : $firstFFID"
    echo "Last  FFID   : $((ffid-1))"
    echo "Missing files: $missing"
    echo "Files QC'd   : $((ffid-firstFFID-missing))"
    echo
    echo Rewinding tape...
    mt -f $tape rewind
    echo Ejecting...
    mt -f $tape eject
} 2>&1 | output

end=$(date +%s)
echo Total time: $(((end - begintime) / 60)) min
