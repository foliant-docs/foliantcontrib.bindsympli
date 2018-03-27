#!/usr/bin/perl


# Global settings and requirements
use strict;
use warnings;
use File::Find;


# Working and cache directories

if(scalar(@ARGV) < 2)
{
    print "Two parameters must be specified: working directory, cache directory\n";
    exit(1);
}

my $working_dir = shift(@ARGV);
my $cache_dir = shift(@ARGV);

$working_dir =~ s/\/+$//;
$cache_dir =~ s/\/+$//;


# Design page URLs file
my $design_urls_file = $cache_dir . '/design_urls.txt';


# Cleanup
if(-e $design_urls_file)
{
    unlink($design_urls_file);
}


# List of Markdown files for processing
my @markdown_files = ();


# Hash for URLs of design pages
my %design_urls = ();


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


    # Reading source file line-by-line, collecting URLs of design pages in Sympli

    open(MARKDOWN_SRC, $markdown_file);

    while(my $markdown_src_line = <MARKDOWN_SRC>)
    {
        $markdown_src_line =~ s/\r//g;

        chomp($markdown_src_line);

        if($markdown_src_line =~ /^\s*!\[[^\[\]]*\]\(https:\/\/app\.sympli\.io\/app#!\/designs\/[0-9a-z\/]+\)\s*$/)
        {
            my ($prefix, $design_url, $postfix) = $markdown_src_line =~ /^(\s*!\[[^\[\]]*\]\()(https:\/\/app\.sympli\.io\/app#!\/designs\/[0-9a-z\/]+)(\)\s*)$/;

            $design_urls{$design_url}++;
        }
    }

    close(MARKDOWN_SRC);
}


# Writing the list of design page URLs into the file

if(scalar(keys(%design_urls)) > 0)
{
    open(DESIGN_URLS, ">$design_urls_file");

    foreach my $design_url (sort({$a cmp $b} keys(%design_urls)))
    {
        print DESIGN_URLS "$design_url\n";
    }

    close(DESIGN_URLS);
}
else
{
    print "No design page URLs found\n";
    exit(1);
}


# Exit
exit(0);
