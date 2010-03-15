require 'rubygems'
require 'spec'
require 'rest_client'
require 'json'
require 'rdf'
require 'rdf/trix'
require 'rdf/ntriples'

def server_get(path, opts = {})
  RestClient.get "#{ENV['sesame_server']}/#{path}", opts
end

def get(path,opts = {})
  RestClient.get "#{ENV['sesame_server']}/repositories/#{ENV['repository']}/#{path}", opts
end


statement_formats = {
  "RDF/XML"   => 'application/rdf+xml',
  "N-Triples" => 'text/plain',
  "Turtle"    => 'application/x-turtle',
  "N3"        => 'application/rdf+n3',
  "TriX"      => 'application/trix',
  "TriG"      => 'application/x-trig' }

subjects   = [nil,'subject']
predicates = [nil,'predicate']
objects    = [nil,'object']
contexts   = [nil,'context']
base_uris  = [nil,'base uri']
describe "A Sesame Server," do

  before :all do
    ENV['sesame_server'] ||= 'localhost:9292'
    ENV['repository'] ||= 'test'

    @repo = RDF::Repository.new

    @contexts
  end

  context "when reporting the protocol version," do
    it "should report version 4" do
      response = server_get "/protocol"
      response.code.should == 200
      response.body.should == "4"
    end

    it "should have a content-type of text/plain" do
      response = server_get "/protocol"
      response.code.should == 200
      response.headers[:content_type].should include "text/plain"
    end
  end


  context "when listing repositories," do

    it "should return XML bindings by default" do
      response = server_get "/repositories"
      response.code.should == 200
      response.headers[:content_type].should include "application/sparql-results+xml"
    end

    it "should return JSON bindings on request" do
      response = server_get "/repositories", :accept => 'application/sparql-results+json'
      response.code.should == 200
      response.headers[:content_type].should include "application/sparql-results+json"
    end

    it "should list our test repository" do
      response = server_get "/repositories", :accept => 'application/sparql-results+json'
      response.code.should == 200
      json = JSON.parse response.body
      json['results']['bindings'].map { | r | r["id"]["value"] }.should include ENV['repository']
    end

    it "should allow writing to our test repository" do
      response = server_get "/repositories", :accept => 'application/sparql-results+json'
      response.code.should == 200
      json = JSON.parse response.body
      repo = json['results']['bindings'].find { | r | r["id"]["value"] == ENV['repository'] }
      repo["writable"]["value"].should == "true"
    end
  end
  
  context "when querying the repository," do
    it "should default to RDF/XML"
  end

  ['post','put'].each do | verb |
    context "when adding statements with #{verb}," do
      contexts.each do | rdf_context |
        context "with a context of #{rdf_context.nil? ? 'nil' : rdf_context}," do
          base_uris.each do | base_uri |
            context "with a base URI of #{base_uri.nil? ? 'nil' : base_uri}," do
              it "should use RDF/XML by default"
              statement_formats.each do | format |
                if verb == 'post'
                  it "should append to the repository using #{format}"
                elsif verb == 'put'
                  it "should replace the repository using #{format}"
                end
              end
            end
          end
        end
      end
    end
  end

  ['get','delete','size'].each do | verb |
    context "when using #{verb}," do

      before :each do
        # setup repository
      end

      subjects.each do | subject |
        context "with a subject of #{subject.nil? ? 'nil' : subject}," do
          predicates.each do | predicate |
            context "with a predicate of #{predicate.nil? ? 'nil' : predicate}," do
              objects.each do | object |
                context "with an object of #{object.nil? ? 'nil' : object}," do
                  contexts.each do | rdf_context |
                    context "with a context of #{rdf_context.nil? ? 'nil' : rdf_context}," do
                      if verb == 'get'
                        it "should default to RDF/XML"
                        it "should return the correct statements without inferred statements (using RDF/XML)"
                        statement_formats.keys.each do | format |
                          it "should #{verb} the correct statements in #{format}"
                        end
                      elsif verb == 'delete'
                        it "should #{verb} the correct statements"
                      elsif verb == 'size'
                        it "should return the correct size"
                      end
                    end
                  end
                end
              end
            end
          end
        end
      end
    end
  end
end


