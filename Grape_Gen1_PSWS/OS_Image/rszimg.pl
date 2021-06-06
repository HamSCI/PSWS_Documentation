#!/usr/bin/perl
# N8OBJ 4-7-2021
#
# resize Raspian OS image of SD card (mine was a 32GB uSD card)
#
# this raw image is obtained from linux cmd
#   sudo dd bs=512 if=/dev/sdb of=Grape1_OS_Gen1.img
#
#   where /dev/sdb is the mounted uSD card (NO # following /dev/sdb - you want the whole card image)
#
# My results:
# $ sudo dd bs=512 if=/dev/sdb of=Grape1_OS_Gen1.img
#   62521344+0 records in
#   62521344+0 records out
#   32010928128 bytes (32 GB, 30 GiB) copied, 339.402 s, 94.3 MB/s
#
# resulting file:
#   -rw-r--r-- 1 root  root  32010928128 Apr  7 00:31 Grape1_OS_Gen1.img
#
#
# cmd to shrink the original image file is [you need full path to the file which will be overwritten] 
#
#   sudo perl ~/RasPi/OSimage/rszimg.pl ~/RasPi/OSimage/Grape1_OS_Gen1.img
#
# My Results:
#  $ sudo perl ~/RasPi/OSimage/rszimg.pl ~/RasPi/OSimage/Grape1_OS_Gen1.img
#
#    Grape1_OS_Gen1.img:
#    ===================
#    Old size - 30527 MB (29.81 GB)
#    New size - 11663 MB (11.39 GB)
#    Image file was reduced by 18864 MB (18.42 GB)
#
# resulting new file size:
#   -rw-r--r-- 1 root  root  12230557697 Apr  7 00:32 Grape1_OS_Gen1.img
#
#  After .zip compression file size is:
#
#   -rw-rw-r-- 1 n8obj n8obj  5955515111 Apr  7 00:59 Grape1_OS_Gen1.img.zip
#
use utf8;
use 5.010;
use strict;
#use autodie;
use warnings;
#use diagnostics;

my $who = `whoami`;

if ($who !~ /root/)
{

	print "This should be run as root or with the sudo command.\n";
	exit 1;

}

if (!$ARGV[0])
{
	
	print "No image file given.\n";
	exit 1;
	
}

my $image = $ARGV[0];

if ($image !~ /^\//)
{

	print "Please enter full path to image file.\n";
	exit 1;
	
}

if (! -e $image)
{

	print "$image does not exist.\n";
	exit 1;
	
}

my @name = split (/\//, $image);
print "\n$name[(scalar @name) - 1]:\n";
print "=" x (length ($name[(scalar @name) - 1]) + 1) . "\n";

my $info = `parted -m $image unit B print | grep ext4`;

(my $num, my $start, my $old, my $dummy) = split (':', $info, 4);
chop $start;
chop $old;
printf "Old size - %d MB (%1.2f GB)\n", int ($old / 1048576), ($old / 1073741824);

my $loopback = `losetup -f --show -o $start $image`;
chop $loopback;

`e2fsck -p -f $loopback`;

if ($? != 0)
{

	print "There was an error in the file system that can't be automatically fixed... aborting.\n";
	`losetup -d $loopback`;
	exit 1;

}

$info = `resize2fs -P $loopback 2>&1`;

($dummy, my $size) = split (': ', $info, 2);
chop $size;
$size = $size + 1024;

`sudo resize2fs -p $loopback $size 2>&1`;
sleep 1;
`losetup -d $loopback`;

$size = ($size * 4096) + $start;

`parted $image rm $num`;
`parted -s $image unit B mkpart primary $start $size`;

$size = $size + 58720257;
printf "New size - %d MB (%1.2f GB)\n", int ($size / 1048576), ($size / 1073741824);

`truncate -s $size $image`;

my $diff = $old - $size;
printf "Image file was reduced by %d MB (%1.2f GB)\n", int ($diff / 1048576), ($diff / 1073741824);

exit 0;

