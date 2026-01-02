{
  "autoscale.min_workers": {
    "type": "range",
    "minValue": 1,
    "maxValue": ${max_workers}
  },
  "autoscale.max_workers": {
    "type": "range",
    "minValue": 1,
    "maxValue": ${max_workers}
  },
  "num_workers": {
    "type": "range",
    "minValue": 1,
    "maxValue": ${max_workers}
  },
  "autotermination_minutes": {
    "type": "range",
    "minValue": 10,
    "maxValue": ${max_autotermination_minutes},
    "defaultValue": ${max_autotermination_minutes}
  },
  "node_type_id": {
    "type": "allowlist",
    "values": ${jsonencode(allowed_node_types)},
    "defaultValue": "${default_node_type}"
  },
  "driver_node_type_id": {
    "type": "allowlist",
    "values": ${jsonencode(allowed_node_types)},
    "defaultValue": "${default_node_type}"
  },
  "custom_tags.owner": {
    "type": "fixed",
    "value": "${default_owner_tag}"
  },
  "custom_tags.cost_center": {
    "type": "unlimited",
    "defaultValue": "${default_cost_center_tag}"
  },
  "custom_tags.env": {
    "type": "fixed",
    "value": "${environment}"
  }
}
