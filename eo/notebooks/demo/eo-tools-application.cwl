#!/usr/bin/env cwl-runner

class: CommandLineTool
cwlVersion: v1.0

label: "Application to process Sentinel products ESA's Snap software thought a python wrapper."

requirements:
  DockerRequirement:
    dockerPull: registry.gitlab.com/crim.ca/public/daccs/daccs/daccs-eo-tools:0.1.1
inputs:
  command:
    type: string
    inputBinding:
      position: 1
  source:
    type: File[]
    inputBinding:
      position: 2
      prefix: --source
  output_name:
    type: string?
    inputBinding:
      position: 3
      prefix: --output
  dem:
    type: string?
    inputBinding:
      position: 4
      prefix: --dem
  polarization:
    type: string?
    inputBinding:
      position: 5
      prefix: --polarization
  subswath:
    type: string?
    inputBinding:
      position: 6
      prefix: --subswath
  refband:
    type: string?
    inputBinding:
      position: 7
      prefix: --refband

outputs:
  output:
    type: File
    outputBinding:
      glob: $(runtime.outdir)/*.nc

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
