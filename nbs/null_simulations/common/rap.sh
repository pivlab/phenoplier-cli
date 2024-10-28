#!/bin/bash

run_cloud_workstation() {
  local max_session_length="$1"
  local session_name="$2"
  local tag="$3"
  local instance_type="$4"

  dx run app-cloud_workstation \
    -imax_session_length="${max_session_length}" \
    --brief -y \
    --name "${session_name}" \
    --tag "${tag}" \
    --instance-type "${instance_type}" \
    --priority "normal"
}
