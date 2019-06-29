require 'pragmatic_segmenter'

# text = "Hello world. My name is Mr. Smith. I work for the U.S. Government and I live in the U.S. I live in New York."

path = ARGV[0]
text = File.read(path)
ps = PragmaticSegmenter::Segmenter.new(text: text)
for line in ps.segment
	puts line
end
