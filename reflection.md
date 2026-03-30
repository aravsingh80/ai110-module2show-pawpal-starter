# PawPal+ Project Reflection

## 1. System Design

**Core actions a user should be able to perform**

- A user should be able to add a pet or add multiple pets
- A user should be able to view their daily tasks
- A user should be able to schedule a task

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design included four main classes: Owner, Pet, Task, and Scheduler. The Owner class represents the user and stores basic information like their name, email, available time per day, and the list of pets they own. It also includes methods for adding pets and checking how much time they have available. The Pet class represents each pet and stores details like its name, species, age, preferences, and the tasks assigned to it. It also has methods for adding tasks and getting tasks based on priority. The Task class represents activities like feeding or walking a pet, with attributes such as title, duration, priority, category, time of day, and whether the task is completed. It also includes methods for calculating priority and marking a task as complete. Finally, the Scheduler class organizes tasks across pets and generates a daily schedule while making sure the tasks fit within the owner’s available time.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
