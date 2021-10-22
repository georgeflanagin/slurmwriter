slurmwriter()
{
    export oldsw="$sw"
    export sw=/usr/local/sw
    command pushd $sw/slurmwriter > /dev/null
    clear
    python slurmwriter.py $@
    command popd > /dev/null
    export sw=$oldsw
}

slurmwriter
