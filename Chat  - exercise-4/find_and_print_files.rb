#!/usr/bin/env ruby

require "find"

file_name = ARGV[0]

if file_name.nil? || file_name.empty?
  warn "Usage: ruby find_and_print_files.rb FILE_NAME"
  exit 1
end

matches = []

Find.find(__dir__) do |path|
  next unless File.file?(path)
  next unless File.basename(path) == file_name

  matches << path
end

if matches.empty?
  puts "No files named #{file_name.inspect} found in #{__dir__}."
  exit 0
end

matches.sort.each do |path|
  puts "\n--- #{path} ---"
  print File.read(path)
  puts unless File.read(path).end_with?("\n")
end