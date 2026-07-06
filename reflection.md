# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For my initial UML design, I was thinking of creating a task class and having walks, feeding, meds, enrichment, grooming, etc. as child classes. For example, the tasks class will include the time, date, and/or description of the task. These classes will include methods that allow the task to be added/edited/deleted. Additionally, I thought about creating a daily plan class which would include variables of time availablility, priority, and owner preferences. In terms of methods, I would have this class allow tasks to be scheduled for a certain day and time as well as removing/deleting a previously added task event.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

My design didn't change too drastically, but my ai coding assistant recommended that I included logic that made sure the scheduler is able to retrieve the proper information/tasks from the owner's pets. For example, methods such as collect_tasks() were included. 

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

Some constraints that my scheduler considered was time and priority. I decided that the constraint that mattered most was the priority of the task, because if a task is urgent/has high priority, it should be done/completed regardless of when it happens.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

One tradeoff that my scheduler makes is that it is not optimal because it uses a greedy strategy/algorithm. This means that while this algorithm is not the best, it is still able to perform its job because the scale of the list of tasks is tiny. 

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used AI tools during this project for most of the designing and implementation process. Prompts such as asking to explain the given code or to brainstorm ideas for completing a certain task/method was very helpful.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

One moment where I did not accept an AI suggestion as-is when it tried to recommend another class for implementing the back-end logic of the scheduling process. I felt that this would make the code much more complex than it needed to be and I instead tried to reroute it so that this logic can be implemented in the scheduler class. 

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

I tested behaviors such as adding owner, pets, tasks, and generating the schedule. These tests were important because it ensured that the major features of this program worked properly.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I am confident that my scheduler works correctly. I believe that for the most part, my scheduler should do what is expected to do. If I had more time, I would try to test for some other edge cases such as attempting to add a task that is in between another task that was already added. 

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

Some parts of this project that I was most satisfied with are the UML designs as well as the code implementation.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

If I had the chance, I would try to improve the UI of the app.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

One thing that I learned about designing systems and working with AI on this project is that we need to always verify before moving forward with the process. Mistakes can happen when using AI and as the human, it is important to take a look at what AI produced before marking it as "correct" or "sufficient" for the job.
