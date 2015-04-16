#!/bin/bash
#
# Copies SEG-D data files from one directory to another, as acquisition proceeds

function msg() {
  date=$(date "+%Y-%m-%d %H:%M:%S %Z")
  echo "$date - $@" 1>&2
}

function die () {
  msg "$@"
  exit 100
}

RSYNC="/usr/bin/rsync -hpa --progress --ignore-existing --size-only"
EOL=EOL.ffid

if [[ $# -ne 1 ]]; then
    echo
    echo "Usage: $0 destination"
    echo
    echo "\"destination\" must end in .segd"
    echo "If it already exists, then it must be a directory."
    echo
    echo "Example: $0 /asima/realtime.segd"
    echo
    exit 1
fi

source_dir=/argus/raid2
if [[ ! -d $source_dir ]]; then
    die "Source directory \"$source_dir\" doesn't exist."
fi

dest_dir=`readlink -f "$1"`

if [[ "${dest_dir%.segd}" == "$dest_dir" ]]; then
    die "The destination directory must end in .segd"
fi
if [[ ! -e $dest_dir ]]; then
    mkdir "$dest_dir" || die "Unable to create output directory $dest_dir"
elif [[ ! -d $dest_dir ]]; then
    die "Destination directory \"$dest_dir\" already exists, but isn't a directory."
fi

ls -1dtr "$source_dir/"*.* | cut -d / -f 4

echo -n "Please choose a line to process: "
read argus_sail_dir

if [[ ! -d "$source_dir/$argus_sail_dir" ]]; then
    die "$argus_sail_dir doesn't exist inside $source_dir"
fi

# remove the trailing .*
sail_dir=${argus_sail_dir%.*}
echo -n "To write to a different line name, provide it here [or press Enter for $sail_dir]: "
read read_tmp
if [[ -n "$read_tmp" ]]; then
    sail_dir=$read_tmp
fi

source_dir="$source_dir/$argus_sail_dir"
dest_dir="$dest_dir/$sail_dir"
msg "Source     : $source_dir"
msg "Destination: $dest_dir"
msg ""
msg "Copying will begin in a few seconds; Ctrl-C to abort."
sleep 3

mkdir -p "$dest_dir"
cd $source_dir

# Wait for the first file to appear
ffid=
while [[ 1 ]]; do
    ffid=`ls -1 *.ffid | head -1`
    if [[ $? -ne 0 ]]; then
        sleep 1
        continue
    fi

    ffid=${ffid%.ffid}
    ffid=$((10#$ffid)) # force base-10
    break
done

msg "First FFID is $ffid"

for (( ; ; ffid=ffid + 1 )); do
    file=`printf %08d.ffid $ffid`
    next_file=`printf %08d.ffid $((ffid + 1))`
    next_file01=`printf %08d.ffid $((ffid + 1))`
    next_file02=`printf %08d.ffid $((ffid + 2))`
    next_file03=`printf %08d.ffid $((ffid + 3))`
    next_file04=`printf %08d.ffid $((ffid + 4))`
    next_file05=`printf %08d.ffid $((ffid + 5))`
    sleeps=0

    # Unfortunately, given the way that argus writes its files, the only way to know for sure
    # that a file has finished writing is if the next one (or the EOL marker) has appeared.
    while [[ ! -e "$next_file" && ! -e "$EOL" ]]; do
        sleep 1
        sleeps=$((sleeps + 1))
        if (( sleeps % 15 == 0 )); then
            msg "Still waiting for $next_file after $sleeps seconds ..."
        fi
                   
        if [[ -e "$next_file01" ]]; then
            next_file="$next_file01"
        elif [[ -e "$next_file02" ]]; then
            next_file="$next_file02"
        elif [[ -e "$next_file03" ]]; then
            next_file="$next_file03"
        elif [[ -e "$next_file04" ]]; then
            next_file="$next_file04"
        elif [[ -e "$next_file05" ]]; then
            next_file="$next_file05"
        fi 
    done

    if [[ -e "$EOL" ]]; then
        msg "EOL marker found -- doing a final rsync, then exiting."
        $RSYNC "$source_dir"/ "$dest_dir"/
        break
    fi

    if [[ ! -e "$file" ]]; then
        msg "$next_file exists, but $file doesn't?  Leaving a gap where $file should be ..."
        continue
    fi

    if [[ -e "$dest_dir/$file" ]]; then
        msg "Not copying $file -- it already exists in the destination."
        continue
    fi

    $RSYNC "$source_dir/$file" "$dest_dir/$file"
    # Ctrl-c doesn't seem to cause rsync to exit with a non-zero RC (!?), so we have to
    # do this nonsense.
    if [[ ! -f $dest_dir/$file ]]; then
        if [[ -s $source_dir/$file ]]; then
            die "rsync failed or was canceled.  Aborting."
        else
            msg "Zero sized source $file -- skipping"
        fi
    fi
done

exit 0
