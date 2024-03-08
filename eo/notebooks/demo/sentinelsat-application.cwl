#!/usr/bin/env cwl-runner

# Changes to this application should also be mirrored in config/sentinelsat/applications/sentinelsat-application.cwl
class: CommandLineTool
cwlVersion: v1.0

label: "Application to batch download Sentinel products."


requirements:
  DockerRequirement:
    dockerPull: registry.gitlab.com/crim.ca/public/daccs/daccs/daccs-eo-sentinelsat:0.2.1
arguments: [ "-d" ]
inputs:
  credentials:
    type: File
    inputBinding:
      position: 1
      prefix: --credentials
  image:
    type: string[]
    inputBinding:
      prefix: --name
      itemSeparator: ","
      position: 2

outputs:
  download_status:
    type: File
    outputBinding:
      glob: $(runtime.outdir)/download_succeeded.txt
  output:
    type: Directory
    outputBinding:
      glob: $(runtime.outdir)

# Metadata is not visible on Weaver once application is deployed; this is mainly to conserve the information
s:author:
  - class: s:Person
    s:email: francis.pelletier@crim.ca
    s:name: Francis Pelletier
# Update version manually after changes to CWL application changes
s:version: 0.1.0

$namespaces:
  s: https://schema.org/

$schemas:
  https://schema.org/version/latest/schemaorg-current-http.rdf
  