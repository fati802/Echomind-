# EchoMind Ground-Truth Q&A Set (Demo Contingency Dataset)

This document contains 10 ground-truth question-and-answer pairs based on the synthetic demo data seeded by [seed_data.py](file:///f:/Echomind/backend/scripts/seed_data.py). This set serves as verification for the retrieval-augmented generation (RAG) backend and as a contingency plan for demo testing.

---

## Ground-Truth Q&A Pairs

### 1. Where are my glasses?
* **Expected Answer**: Your glasses were placed on the bedside table at 09:30 PM by you. (Prior events: placed on kitchen shelf at 08:15 AM, picked up at 12:15 PM, placed on dining table at 04:30 PM, and picked up from dining table by caregiver at 07:15 PM).
* **Live API Response (July 08, 2026)**:
  ```json
  {
    "answer": "Your glasses was placed by patient in/on the kitchen shelf at 08:15 AM on July 08, 2026. Your glasses was picked up by patient in/on the kitchen shelf at 12:15 PM on July 08, 2026. Your glasses was placed by patient in/on the dining table at 04:30 PM on July 08, 2026. I think I saw your glasses picked up by caregiver in/on the dining table at 07:15 PM on July 08, 2026, but I'm not fully sure — you may want to double check. Your glasses was placed by patient in/on the bedside table at 09:30 PM on July 08, 2026.",
    "mode": "mock_fallback"
  }
  ```
  *(Note: Fell back to mock_fallback due to Fireworks read operation timeout for this longer prompt during cold-start)*

---

### 2. Who gave me my medicine?
* **Expected Answer**: The caregiver handed over your medicine box to you at 10:30 AM in the living room, and again at 02:15 PM in the kitchen.
* **Live API Response (July 08, 2026)**:
  ```json
  {
    "answer": "The user is asking who gave them their medicine. Looking at the event log, I can see that a \"caregiver\" handed over the medicine box at 10:30 AM in the living room and again at 2:15 PM in the kitchen. Both events have Certainty: Certain, so I should state this plainly without hedging.\n\nThe events show:\n- At 10:30 AM: caregiver handed_over the medicine box in the living room\n- At 2:15 PM: caregiver handed_over the medicine box in the kitchen\n\nSo the caregiver gave them their medicine. I should mention both instances since both involved the caregiver handing over the medicine box.",
    "mode": "fireworks_fallback"
  }
  ```

---

### 3. Did I take my medicine today?
* **Expected Answer**: Yes, you received/took the medicine box from the caregiver twice today: at 10:30 AM in the living room, and at 02:15 PM in the kitchen.
* **Live API Response (July 08, 2026)**:
  ```json
  {
    "answer": "The user is asking if they took their medicine today. Let me look at the event log to see what information is available.\n\nThe events show:\n1. At 08:30 AM, caregiver placed the medicine box on the kitchen shelf (Certain)\n2. At 10:30 AM, caregiver handed over the medicine box in the living room (Certain)\n3. At 02:15 PM, caregiver handed over the medicine box in the kitchen (Certain)\n4. At 10:15 PM, someone observed the medicine box on the kitchen shelf (Certain)\n\nThe events show that the medicine box was handed over to the user twice (at 10:30 AM and 2:15 PM)...",
    "mode": "fireworks_fallback"
  }
  ```

---

### 4. Where are my keys?
* **Expected Answer**: Your keys were placed on the bedside table at 11:00 PM. (Prior events: placed on hallway table at 09:15 AM, picked up at 05:45 PM).
* **Live API Response (July 08, 2026)**:
  ```json
  {
    "answer": "The user is asking where their keys are. Let me look at the event log to find the most recent event about the keys.\n\nThe events are:\n1. At 09:15 AM on July 08, 2026: patient placed the keys in/on the hallway table. [Certainty: Certain]\n2. At 05:45 PM on July 08, 2026: patient picked_up the keys in/on the hallway table. [Certainty: Certain]\n3. At 11:00 PM on July 08, 2026: patient placed the keys in/on the bedside table. [Certainty: Certain]\n\nThe most recent event is at 11:00 PM where the patient placed the keys on the bedside",
    "mode": "fireworks_fallback"
  }
  ```

---

### 5. Where is the remote?
* **Expected Answer**: The remote was picked up from the couch at 08:00 PM. (Prior events: placed on study table at 09:45 AM, picked up from study table at 11:00 AM (Unsure/Likely), and placed on the couch at 03:15 PM (Unsure/Likely)).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*

---

### 6. Where did I leave my mug?
* **Expected Answer**: Your mug was placed in/on the kitchen sink at 06:30 PM. (Prior events: placed on the dining table at 08:45 AM, and picked up from the dining table at 01:30 PM).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*

---

### 7. What did the caregiver do today?
* **Expected Answer**: The caregiver placed the medicine box on the kitchen shelf at 08:30 AM, handed over the medicine box in the living room at 10:30 AM and in the kitchen at 02:15 PM, and picked up the glasses from the dining table at 07:15 PM (Unsure/Hedging).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*

---

### 8. Did someone find my glasses this evening?
* **Expected Answer**: Yes, it looks like the caregiver picked up your glasses from the dining table at 07:15 PM, but I'm not fully sure — you may want to double check. (This event has 0.55 confidence, testing the hedging rules).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*

---

### 9. Did anyone observe the medicine box late tonight?
* **Expected Answer**: Yes, the medicine box was observed on the kitchen shelf at 10:15 PM by an unidentified person (actor was null).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*

---

### 10. Where did I have the remote in the afternoon?
* **Expected Answer**: In the afternoon, it looks like/it seems the remote was placed on the couch at 03:15 PM. (This event has 0.60 confidence, testing the hedging rules).
* **Live API Response (July 08, 2026)**: *(Not queried manually)*
