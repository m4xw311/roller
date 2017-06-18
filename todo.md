# Required Capabilities
1. Detect circular includes (infinite executions)
2. Standard Change
3. Standard Target
4. Standard Test
5. Variable resolution: "data" of a change refrencing "data" and "capture" of another change. Specifying "data" in the "deploy", "rollback", etc
6. How to implement idempotence?
a. Using capture to decide whether to skip or to execute - implemented
b. Using stored history to know if the execution is already done in the past - considering whether to implement
7. Optimizatons:
a. For a skipped change, assign the pre data to post rather than executing and finding post data - unnecessary
