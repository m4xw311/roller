# Required Capabilities
- [ ] Standard Target
- [ ] Standard Test
- [ ] Variable resolution: "data" of a change refrencing "data" and "capture" of another change. Specifying "data" in the "deploy", "rollback", etc
- [x] Detect circular includes (infinite executions) ; also detects duplication of a change name in a change group or duplication of group name in a change script
- [x] Standard Change
- [ ] Implement idempotence
-  - [x] Using capture to decide whether to skip or to execute - implemented
-  - [ ] Using stored history to know if the execution is already done in the past - considering whether to implement
- [ ]  For a skipped change, assign the pre data to post rather than executing and finding post data - unnecessary

