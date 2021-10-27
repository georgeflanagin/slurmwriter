slurmwriter()
{
    location=/tmp/$(whoami).recent
    rm -f $location
    export oldsw="$sw"
    export sw=/usr/local/sw
    command pushd $HOME/slurmwriter > /dev/null
    clear
    python slurmwriter.py $@
    command popd > /dev/null
    export sw=$oldsw
    
    location=/tmp/$(whoami).recent
    if [ -f $location ]; then
        vim $(cat $location)
    fi
}

slurmwriter
