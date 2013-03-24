#!/bin/bash

# Downloads the mirrorlist by country, with Server ordered by score.
# Requires to give it as parameter the country code (e.g. USA -> US),
# which is not available until Timezone screen.

COUNTRY_MIRRORLIST='/tmp/country-mirrorlist'
TMP_MIRRORLIST='/tmp/tmp-mirrorlist'
ORIG_MIRRORLIST='/etc/pacman.d/mirrorlist'
MIRRORLIST='/tmp/mirrorlist'

function get_mirrorlist(){
    wget -q -O ${COUNTRY_MIRRORLIST} https://www.archlinux.org/mirrorlist/?country=${COUNTRY_CODE}&protocol=http&ip_version=4&use_mirror_status=on 2>/dev/null
}

function generate_new_mirrorlist(){
    TOTAL_LINES=`wc -l ${COUNTRY_MIRRORLIST}|cut -f 1 -d ' '`
    HEADER_LINES=4

    let MIRRORS_LINES=$TOTAL_LINES-$HEADER_LINES

    #echo "# Selected mirrors by country on top" > ${TMP_MIRRORLIST}
    #echo "# File generated by Cnchi Installer" >> ${TMP_MIRRORLIST}
    #echo "#" >> ${TMP_MIRRORLIST}
    tail -n ${MIRRORS_LINES} ${COUNTRY_MIRRORLIST} > ${TMP_MIRRORLIST}

    sed -i "s/#Server/Server/" ${TMP_MIRRORLIST}

    cat ${TMP_MIRRORLIST} ${ORIG_MIRRORLIST} > ${MIRRORLIST}
}
    

COUNTRY_CODE=$1

get_mirrorlist
generate_new_mirrorlist

cp ${MIRRORLIST} ${ORIG_MIRRORLIST}

