# Kubernetes probe checklist for AI services

_Keep a slow dependency from restarting every pod_  
@demotoprod · CHECKLIST · September 2026

A liveness probe that checks a dependency turns a slow database into a restart storm: every replica fails the same probe in the same window, and the kubelet restarts them all together. The demo never shows it, because the demo ran one pod. Every default and behaviour below is from the Kubernetes documentation; nothing here is a vendor claim. Five checks; the first two are an afternoon's work.

**Prove it in two commands**

```
kubectl get pods                 # RESTARTS rises on every replica in the same minute
kubectl describe pod <pod>       # Events: "Liveness probe failed: ..." - then open the probe's handler
```

- [ ] **1. Liveness checks only the process**

  **Why.** The kubelet restarts a container when its liveness probe fails three times in a row, probing every ten seconds with a one-second timeout by default. Point that probe at an endpoint that calls your database, vector store or model server, and one thirty-second stall fails it on every replica at once, so every replica restarts together. Capacity goes to zero while the dependency was only slow.

  **The check.**
  - Open every livenessProbe. If its handler touches anything over the network, move that check out.
  - Liveness answers one question: can this process respond at all?

  Source: [Kubernetes documentation, Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

- [ ] **2. Dependency checks live in readiness**

  **Why.** A failing readiness probe marks the pod unready and takes it out of Service traffic; it does not restart the container. For an AI service that holds a model in memory, that is the difference between a pause and a cold start.

  **The check.**
  - Give the pod two endpoints: /livez (process only) and /readyz (database, vector store, model loaded).
  - The pod leaves traffic while a dependency is down and returns the moment it is back, model still loaded.

  ```
  livenessProbe:  { httpGet: { path: /livez,  port: 8080 } }   # process only, no I/O
  readinessProbe: { httpGet: { path: /readyz, port: 8080 } }   # database, vector store, model loaded
  ```

  Source: [Kubernetes documentation, Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

- [ ] **3. Slow-loading models get a startup probe**

  **Why.** Liveness and readiness checks do not start until the startup probe has succeeded. The documentation's rule: set failureThreshold x periodSeconds long enough to cover the worst-case startup time (its example allows 30 x 10 = 300 seconds).

  **The check.**
  - Time your worst cold start, weights downloaded, loaded and warmed, and size the startup probe to cover it.
  - Do not stretch the liveness probe's initial delay instead.

  Source: [Kubernetes documentation, Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

- [ ] **4. Probe handlers are fast and in-process**

  **Why.** An HTTP probe that answers after its timeout counts as a failure, whatever it would have returned. The default timeout is one second.

  **The check.**
  - Keep the liveness handler constant-time and free of I/O.
  - If it cannot answer inside the timeout under peak load, fix the handler before you raise the timeout.

  Source: [Kubernetes documentation, Configure Liveness, Readiness and Startup Probes](https://kubernetes.io/docs/tasks/configure-pod-container/configure-liveness-readiness-startup-probes/)

- [ ] **5. A restart storm pages someone**

  **Why.** One restart is noise; every replica restarting inside the same minute usually means something they all share, and the events say whether it was the liveness probe. kube-state-metrics exposes restarts per container as kube_pod_container_status_restarts_total.

  **The check.**
  - Alert when restarts rise on several replicas of one Deployment within the same window.
  - Link the alert to the two commands on this page.

  Source: [kube-state-metrics (pod metrics documentation in the repository)](https://github.com/kubernetes/kube-state-metrics)

## Work it in this order

| # | Control | Effort | Impact |
|---|---|---|---|
| 1 | Move dependency checks out of every liveness probe | 1-2 hours | Critical |
| 2 | Add a readiness endpoint that checks the dependencies | 2-4 hours | Critical |
| 3 | Size a startup probe to the worst cold start | 2-4 hours | High |
| 4 | Alert on restarts across replicas | half a day | High |
| 5 | Time the probe handlers under peak load | half a day | Medium |

Effort figures are planning estimates for a team that already runs Kubernetes, not measurements. Everything else on this page is from the Kubernetes documentation.

Want this as a one-page PDF? Email hello@indica-tech.com with the word CHECKLIST in the subject. On the videos, the same word in a comment does the same.

_Kubernetes probe checklist for AI services · September 2026 · @demotoprod_
