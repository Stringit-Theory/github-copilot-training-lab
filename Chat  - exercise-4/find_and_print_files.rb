# Searches for files by name or prints every regular file under the script's directory.
# The --all option enables printing the complete folder tree.
# frozen_string_literal: true

require "find"

def print_files(paths)
  paths.sort.each do |path|
    puts "\n--- #{path} ---"
    contents = File.read(path)
    print contents
    puts unless contents.end_with?("\n")
  end
end

def print_all_files(directory)
  paths = []

  Find.find(directory) do |path|
    paths << path if File.file?(path)
  end

  print_files(paths)
end

file_name = ARGV[0]

if file_name == "--all"
  print_all_files(__dir__)
  exit 0
end

if file_name.nil? || file_name.empty?
  warn "Usage: ruby find_and_print_files.rb FILE_NAME|--all"
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

print_files(matches)