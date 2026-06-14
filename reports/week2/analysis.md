## Learning points

### User stories
We learned to write short, user‑focused stories that capture "what" the user needs, not "how" the system implements it.  

### Prioritization
For prioritization we use MoSCoW system. 
This prevented us from overbuilding the MVP.

### Prototyping
We built only one prototype - Computer prototype. To understend:
1 Check whether the interface is visually and structurally suitable for the customer.
2 Get feedback on the layout of elements, colors, fonts, and labels.
3 Quickly make changes without spending time on programming the logic.

### Interface design and Customer validation of the proposed product interface
We showed frontend mockup to the customer.
The customer acted as a beginner – he is not familiar with the implementation details and looks at the interface as an ordinary user. During the review, he honestly pointed out what exactly and where he found unclear:

-
-
-
-

Based on this feedback, we improved the site:
-
-
-
-

### MVP v0 deployment
Our MVP v0 became a frontend site with minimal backend, which:

- Allows users to register (create an account, log in).
- Can send notifications, but only manually – by clicking the "send test notification" button (simulation).


## Validated assumptions

1)See on the ticket date and time of the match to understand could user go there. - accepted.
2)See on the site list of all teams of KHL to choose which team user can subscribe to. -accepted.
3)Choose on the site specific stadium too user understanding can he visit matche or not. rejected.

## Needs clarification

1)Questions to customer -

2)Technical Risks - The parser may not work on some websites

## 6.4 Planned Response

### 1. Interface improvements based on customer feedback

- What we learned:
- What we are changing:

### 2. Display the full list of KHL teams for subscription
- What we learned: Users need to see all available KHL teams in one place to choose which team they want to subscribe to.
- What we are changing: We will add a page or section showing the complete list of KHL teams. Users can browse the list and subscribe to any team they are interested in.


### 3. Investigating parsing risks
- What we learned: There is a risk that the parser may not work on the KHL website.
- What we are changing: We add a research and prototyping phase for the parser before full development.

