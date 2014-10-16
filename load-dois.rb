# coding: utf-8
require 'httpclient'
require 'uri'
require 'multi_json'

$stdout.sync = true

BAD_DOIS = [
  '10.1371/journal.pone.0006083', # duplicate URI reference
  '10.1371/journal.pone.0033192', # citation with no bib data
  '10.1371/journal.pone.0037874', # bad URI
  '10.1371/journal.pone.0051264', # bad URI
  '10.1371/journal.pone.0055544', # bad URI
  '10.1371/journal.pone.0075957', # bad URI
  '10.1371/journal.pone.0091372', # bad URI
  '10.1371/journal.pone.0100338', # bad URI
  '10.1371/journal.pone.0105142', # bad URI
  '10.1371/journal.pone.0107541'  # duplicate URI reference
]

$new_bad_dois = []

$client = HTTPClient.new
BASE_URL = 'http://api.richcitations.org/papers'
API_KEY = '...'

def encode_uri(uri)
  return nil if uri.nil?
  # properly encode DOI URIs
  md = uri.match(%r{^http://dx.doi.org/(.*)$})
  if md
    doi_enc = URI.encode_www_form_component(md[1])
    "http://dx.doi.org/#{doi_enc}"
  else
    URI.encode(uri)
  end
end

def clean_json(json)
  if json.is_a? Hash
    json.keys.each do |k|
      if (k == 'uri')
        json[k] = encode_uri(json[k])
      else
        clean_json(json[k])
      end
    end
  elsif json.is_a? Array
    json.each do |v|
      clean_json(v)
    end
  end
end

def send_json(doi, json)
  return if BAD_DOIS.member?(doi)
  doi_uri = encode_uri("http://dx.doi.org/#{doi}")
  return if ($client.head(BASE_URL, uri: doi_uri).status == 200)
  clean_json(json)
  doi_uri_enc = URI.encode_www_form_component(doi_uri)
  response = $client.post("#{BASE_URL}?api_key=#{API_KEY}&uri=#{doi_uri_enc}",
                          MultiJson.dump(json),
                          'Content-Type' => 'application/json',
                          'Accept' => 'application/json')
  if (response.status == 201)
    puts doi
  else
    puts "BAD DOI: #{doi}"
    $new_bad_dois.push(doi)
  end
end

def send_file(path)
  path = File.absolute_path(path)
  md = path.match(%r{/(10.1371[^/]+)\.json$})
  if md
    # single file per item style
    doi_enc = md[1]
    doi = doi_enc.gsub(/%2[Ff]/, '/')
    json = MultiJson.load(File.open(path, 'r').read)
    send_json(doi, json)
  else
    # big JSON file style
    json = MultiJson.load(File.open(path, 'r').read)
    json.each do |item|
      doi = item['doi']
      data = item['result']
      send_json(doi, data) if data
    end
  end
end

if ARGV.size > 0 then
  ARGV.each do |path|
    send_file(path)
  end
else
  Dir.glob('/home/egh/tmp/*.json').each do |path|
    send_file(path)
  end
end

puts "got bad dois:"
puts $new_bad_dois.join("\n")
