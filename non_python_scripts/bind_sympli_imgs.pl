#!/usr/bin/perl


# Global settings and requirements
use strict;
use warnings;
use File::Find;
use File::Copy;
use Digest::SHA qw(sha1_hex);


# Working and cache directories, resulting image width, paths to wget and convert

if(scalar(@ARGV) < 3)
{
    print "Three parameters must be specified: working directory, cache directory, resulting image width\nOptional parameters: path to wget, path to convert\n";
    exit(1);
}

my $working_dir = shift(@ARGV);
my $cache_dir = shift(@ARGV);
my $resulting_img_width = shift(@ARGV);
my $overridden_wget_path = shift(@ARGV);
my $overridden_convert_path = shift(@ARGV);

$working_dir =~ s/\/+$//;
$cache_dir =~ s/\/+$//;

my $wget_path = 'wget';
my $convert_path = 'convert';

if(defined($overridden_wget_path))
{
    $wget_path = $overridden_wget_path;
}

if(defined($overridden_convert_path))
{
    $convert_path = $overridden_convert_path;
}


# Image URLs file
my $img_urls_file = $cache_dir . '/img_urls.txt';


# Processing image URLs

if(!(-e $img_urls_file))
{
    print "Image URLs file does not exist\n";
    exit(1);
}


# Hash for image URLs
my %img_urls = ();

my $resulting_img_dir = $working_dir . '/_img_from_sympli';

if (!-d $resulting_img_dir)
{
    mkdir($resulting_img_dir);
}

open(IMG_URLS, $img_urls_file);

while(my $img_urls_line = <IMG_URLS>)
{
    chomp($img_urls_line);

    if($img_urls_line =~ /^\S+\t\S+$/)
    {
        my ($design_url, $img_url) = $img_urls_line =~ /^(\S+)\t(\S+)$/;

        $img_urls{$design_url} = $img_url;

        my $original_img_hash = sha1_hex($img_url);
        my $original_img_path = $cache_dir . '/' . $original_img_hash . '_original.png';

        my $resulting_img_hash = sha1_hex($img_url . ' ' . $resulting_img_width);
        my $resized_img_path = $cache_dir . '/' . $resulting_img_hash . '.png';


        # Downloading the image

        if(!-e $original_img_path)
        {
            system("$wget_path -O $original_img_path $img_url");
        }


        # Resizing the image

        if(!-e $resized_img_path)
        {
            system("$convert_path $original_img_path -resize $resulting_img_width $resized_img_path");
        }


        # Copying the image to the working directory

        my $resulting_img_path = $resulting_img_dir . '/' . $resulting_img_hash . '.png';

        copy($resized_img_path, $resulting_img_path);
    }
}

close(IMG_URLS);


# Replacing image URLs in Markdown files

# List of Markdown files for processing
my @markdown_files = ();


# Finding all '*.md' files in working directory recursively

find(\&wanted, $working_dir);

sub wanted
{
    my $markdown_file_path = $_;
    if((-f $markdown_file_path) && ($markdown_file_path =~ /\.md$/))
    {
        push(@markdown_files, $File::Find::name);
    }
}


# Processing each Markdown file

foreach my $markdown_file (@markdown_files)
{
    my $markdown_dst = '';
    my $rewrite_needed = 0;


    # Reading source file line-by-line, collecting URLs of design pages in Sympli, replacing them with local paths

    open(MARKDOWN_SRC, $markdown_file);

    while(my $markdown_src_line = <MARKDOWN_SRC>)
    {
        $markdown_src_line =~ s/\r//g;

        chomp($markdown_src_line);

        if($markdown_src_line =~ /^\s*!\[[^\[\]]*\]\(https:\/\/app\.sympli\.io\/app#!\/designs\/[0-9a-z\/]+\)\s*$/)
        {
            my ($prefix, $design_url, $postfix) = $markdown_src_line =~ /^(\s*!\[[^\[\]]*\]\()(https:\/\/app\.sympli\.io\/app#!\/designs\/[0-9a-z\/]+)(\)\s*)$/;

            my $local_img_path = $resulting_img_dir . '/' . sha1_hex($img_urls{$design_url} . ' ' . $resulting_img_width) . '.png';

            $markdown_dst .= $prefix . $local_img_path . $postfix . "\n";

            $rewrite_needed = 1;
        }
        else
        {
            $markdown_dst .= "$markdown_src_line\n";
        }

    }

    close(MARKDOWN_SRC);


    # Rewriting Markdown file, if needed

    if($rewrite_needed == 1)
    {
        print "Rewriting the file '$markdown_file'\n";

        open(MARKDOWN_DST, ">$markdown_file");
        print MARKDOWN_DST $markdown_dst;
        close(MARKDOWN_DST);
    }
}


# Exit
exit(0);
