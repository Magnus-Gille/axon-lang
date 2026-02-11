# AXON vs English: Side-by-Side Comparisons

This document demonstrates the efficiency gains of AXON over natural English for agent-to-agent communication. Character counts and approximate token counts (using ~4 chars/token average for English, ~3.5 for AXON due to denser encoding) are provided.

---

## Example 1: Simple Status Query

### English
```
Hello Agent-B, I am Agent-A. Could you please tell me what the current status
of the web-server service is? I need to know if it's running properly and what
the current response time looks like. Thank you.
```
**Characters: 229 | ~57 tokens**

### AXON
```
QRY(@a>@b): status(@web-server)
```
**Characters: 32 | ~9 tokens**

**Savings: 86% characters, ~84% tokens**

---

## Example 2: Status Response

### English
```
Hi Agent-A, this is Agent-B responding to your query about the web-server.
The service is currently healthy and running normally. The uptime is 99.7
percent, and the average response latency is 45 milliseconds. Everything
looks good.
```
**Characters: 248 | ~62 tokens**

### AXON
```
RPL(@b>@a): {status:#healthy, uptime:99.7%, latency:45ms}
```
**Characters: 57 | ~16 tokens**

**Savings: 77% characters, ~74% tokens**

---

## Example 3: Task Delegation with Reasoning

### English
```
Dear Worker Agent, I am the Orchestrator and I need you to process the
customer data batch. Specifically, I'd like you to first fetch the data
from the URL I'm providing, then parse it as JSON format, and finally
store the results in the database. The reason for this task is that we
have a quarterly reporting deadline coming up. Please complete this by
end of day.
```
**Characters: 379 | ~95 tokens**

### AXON
```
[^:2]
REQ(@orchestrator>@worker): fetch("customer-data-url") -> parse(#json) -> store(@db, $result) <- #deadline{type:"quarterly-report"}
```
**Characters: 126 | ~35 tokens**

**Savings: 67% characters, ~63% tokens**

---

## Example 4: Error Report

### English
```
Agent-Caller, I'm sorry but I was unable to complete your request. The
resource you asked about could not be found — I received a 404 error
when trying to access it. Unfortunately, retrying won't help in this
case. However, I would suggest that you try querying the registry service
to find out where the item might have been moved to.
```
**Characters: 335 | ~84 tokens**

### AXON
```
ERR(@service>@caller): {code:404, what:"resource not found", ref:@item, retry:F, suggest:QRY(@caller>@registry):locate(@item)}
```
**Characters: 120 | ~34 tokens**

**Savings: 64% characters, ~60% tokens**

---

## Example 5: Proposal and Counter-Proposal

### English (3-message exchange)
```
Message 1:
"Hi Team-B, this is Team-A. We'd like to propose that we migrate the
database to Server-2. We think the best maintenance window would be
between 2:00 AM and 4:00 AM tonight. What do you think?"

Message 2:
"Hello Team-A, we appreciate the proposal but we have a concern. Our
monitoring data shows that there's a peak load period between 2:00 AM
and 3:00 AM, so that window wouldn't work well. Could we do it between
4:00 AM and 6:00 AM instead?"

Message 3:
"That works for us. We accept your counter-proposal for the 4:00 AM to
6:00 AM window."
```
**Characters: 556 | ~139 tokens**

### AXON (3-message exchange)
```
PRO(@a>@b): {action:#migrate, target:@server-2, window:"02:00-04:00"}
CTR(@b>@a): {action:#migrate, target:@server-2, window:"04:00-06:00"} <- load.peak("02:00-03:00")
ACC(@a>@b): _
```
**Characters: 199 | ~57 tokens**

**Savings: 64% characters, ~59% tokens**

---

## Example 6: Multi-Agent Task Distribution

### English
```
"Attention Workers 1, 2, and 3. I am the Planner agent and I need you
to process a large data set collaboratively. Worker-1, please handle
records 0 through 1000. Worker-2, please handle records 1001 through
2000. Worker-3, please handle records 2001 through 3000. When you're
done, send your results back to me so I can merge them together. Please
complete your portions within 5 minutes."
```
**Characters: 399 | ~100 tokens**

### AXON
```
REQ(@planner>[@w1,@w2,@w3]): {task:#data-process, split:[0..1000,1001..2000,2001..3000], merge:@planner, deadline:300s}
```
**Characters: 113 | ~32 tokens**

**Savings: 72% characters, ~68% tokens**

---

## Example 7: Monitoring Subscription

### English
```
"Hi Monitoring Agent, this is the Dashboard. I'd like to subscribe to
receive metrics updates from the production environment. Please send me
updates every 30 seconds with CPU usage, memory usage, and request rate."
```
**Characters: 232 | ~58 tokens**

### AXON
```
SUB(@dashboard>@monitor): #metrics{src:@prod, interval:30s, fields:[cpu,mem,req_rate]}
```
**Characters: 85 | ~24 tokens**

**Savings: 63% characters, ~59% tokens**

---

## Example 8: Complex Reasoning Chain

### English
```
"I need to inform the administrator about an alert situation. We have
a Level 3 alert because the CPU usage has exceeded 95 percent. The
reason the CPU spiked is because of unusual traffic patterns coming
from the web server, which appear to be related to a possible DDoS
attack that started approximately 10 minutes ago."
```
**Characters: 332 | ~83 tokens**

### AXON
```
[^:3]
INF(@monitor>@admin): #alert{level:3} <- cpu>95% <- #spike{src:@web-server} <- #ddos{confidence:~80%, onset:~10min}
```
**Characters: 113 | ~32 tokens**

**Savings: 66% characters, ~61% tokens**

---

## Summary Table

| Example | English Tokens | AXON Tokens | Savings |
|---------|---------------|-------------|---------|
| Status query | ~57 | ~9 | 84% |
| Status reply | ~62 | ~16 | 74% |
| Task delegation | ~95 | ~35 | 63% |
| Error report | ~84 | ~34 | 60% |
| Negotiation (3 msgs) | ~139 | ~57 | 59% |
| Multi-agent distribution | ~100 | ~32 | 68% |
| Subscription | ~58 | ~24 | 59% |
| Reasoning chain | ~83 | ~32 | 61% |
| **Average** | | | **66%** |

AXON achieves an average of **66% token reduction** compared to natural English, while being completely unambiguous and mechanically parseable.

---

## Ambiguity Elimination Examples

### English (ambiguous)
```
"The agent reported the server with the error"
```
Interpretation A: The agent reported [the server that has the error]
Interpretation B: The agent [reported the server] [using the error as the report]
Interpretation C: The agent reported [to the server] [about the error]

### AXON (unambiguous — each interpretation is a distinct expression)
```
INF(@agent>@admin): {target:@server, issue:#error}         (* Interpretation A *)
INF(@agent>@server): #error                                 (* Interpretation C *)
REQ(@agent>@admin): report(@server, cause:#error)           (* Interpretation B *)
```

### English (ambiguous)
```
"Tell the agents that failed to restart"
```
Interpretation A: Tell [the agents that failed] to restart
Interpretation B: Tell the agents [that they failed to restart]

### AXON (unambiguous)
```
CMD(_>@failed-agents): restart()                            (* Interpretation A *)
INF(_>@agents): restart.status = #failed                    (* Interpretation B *)
```
