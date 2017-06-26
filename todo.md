# Required Capabilities
1. Standard Target
2. Standard Test
3. Variable resolution: "data" of a change refrencing "data" and "capture" of another change. Specifying "data" in the "deploy", "rollback", etc
4. How to implement idempotence?
  i. Using stored history to know if the execution is already done in the past - considering whether to implement

# Required Optimizations
1. For a skipped change, assign the pre data to post rather than executing and finding post data - unnecessary

# Implemented Capabilities
1. Detect circular includes (infinite executions) ; also detects duplication of a change name in a change group or duplication of group name in a change script
2. Standard Change
3. How to implement idempotence?
  i. Using capture to decide whether to skip or to execute - implemented
