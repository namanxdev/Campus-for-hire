# Requirements: Campus-to-Hire Personalization Platform

## 1. Overview

### 1.1 Vision
An AI-driven personalization platform that bridges the gap between campus learning and industry hiring by delivering structured, adaptive, and goal-aligned preparation plans — empowering every student, regardless of background, language, or geography, to become job-ready efficiently.

### 1.2 Problem Statement
Campus students fail to become job-ready efficiently because existing preparation resources are generic, English-centric, and disconnected from individual backgrounds, skill gaps, and real hiring expectations. This leads to extended unemployment, repeated rejection cycles, and disproportionate disadvantage for students from Tier-2/3 colleges and non-English-speaking regions.

### 1.3 Solution
A cloud-native platform built entirely on **AWS** that uses AI/ML to analyze student profiles, job market signals, and learning patterns — then generates personalized roadmaps with daily micro-goals, multi-language support, interview simulation, and adaptive difficulty adjustment.

---

## 2. Target Users

| Persona | Description | Key Needs |
|---------|-------------|-----------|
| **Final-Year CS Student** | B.Tech/BE CS student in last year, basic DSA knowledge, targeting product companies | Role-specific roadmap, interview prep, coding practice |
| **Tier-2/3 College Student** | Limited campus placement exposure, needs structured guidance | End-to-end preparation plan, company-specific prep, confidence building |
| **Non-CS Transition Student** | ECE/EE/Mech student transitioning to tech roles | Foundation building, skill gap identification, accelerated learning paths |
| **Early Professional (0–2 yrs)** | Working professional seeking upskilling or role switch | Flexible scheduling, advanced topics, targeted company prep |
| **Regional Language Student** | Hindi/Tamil/Telugu/Bengali-medium student | Multi-language content, vernacular explanations, translated resources |

---

## 3. User Stories

> Priority levels: **P0** = Must-have (launch blocker), **P1** = Should-have, **P2** = Could-have, **P3** = Won't-have (Phase 1)

---

### 3.1 Student Profile & Onboarding — `P0`

**As a** student,  
**I want to** create a profile with my background, skills, and career goals,  
**So that** the platform can personalize my learning path.

**Acceptance Criteria:**
- 3.1.1 System captures student background (CS/non-CS, current year, college tier, degree, major)
- 3.1.2 System assesses current skill level through an adaptive initial assessment (MCQs + coding challenge) or guided self-evaluation
- 3.1.3 System allows selection of target role from: SDE, Cloud Engineer, Data Analyst, DevOps, QA, ML Engineer, Full-Stack Developer
- 3.1.4 System allows selection of up to 5 target companies with auto-suggest (e.g., Amazon, Google, Microsoft, Flipkart, Infosys)
- 3.1.5 System captures available preparation time (hours per day, days per week, preferred time slots)
- 3.1.6 System supports language preferences: English, Hindi, Tamil, Telugu, Bengali, Marathi (extensible)
- 3.1.7 System allows profile editing and re-assessment at any time
- 3.1.8 Onboarding completes in under 10 minutes with progress indicators

**AWS Dependencies:** Amazon Cognito (auth), Amazon RDS Aurora (profile storage)

---

### 3.2 Personalized Roadmap Generation — `P0`

**As a** student,  
**I want to** receive a customized learning roadmap based on my profile and goals,  
**So that** I can follow a structured path to job readiness.

**Acceptance Criteria:**
- 3.2.1 System generates role-specific roadmap aligned with target job requirements within 30 seconds
- 3.2.2 Roadmap adapts to student's current skill level, background (CS vs non-CS), and college tier
- 3.2.3 Roadmap includes milestones with estimated completion timelines and dependencies
- 3.2.4 System identifies and prioritizes skill gaps using a weighted scoring model based on target role
- 3.2.5 Roadmap adjusts total duration based on available preparation time (hours/day × days/week)
- 3.2.6 System provides at least 2 alternative paths: standard pace and accelerated pace
- 3.2.7 Roadmap respects prerequisite ordering (e.g., arrays before dynamic programming)
- 3.2.8 Student can review, confirm, or request regeneration of roadmap before activation

**AWS Dependencies:** Amazon Bedrock (AI generation), Amazon DynamoDB (roadmap storage), AWS Step Functions (orchestration)

---

### 3.3 Daily Actionable Plans — `P0`

**As a** student,  
**I want to** receive daily micro-goals and tasks,  
**So that** I can make consistent progress without feeling overwhelmed.

**Acceptance Criteria:**
- 3.3.1 System generates daily task lists with specific, actionable items (each 15–60 minutes)
- 3.3.2 Total task time ≤ student's configured available hours for that day
- 3.3.3 System balances task types: minimum 2 categories per day (theory, coding practice, review, interview prep, project work)
- 3.3.4 Daily plans include direct links to learning resources, coding problems, and review materials
- 3.3.5 System sends push notifications and email reminders for daily goals
- 3.3.6 Students can mark tasks as complete, skip (with reason), or reschedule
- 3.3.7 Plans auto-generate at midnight in the student's timezone
- 3.3.8 Incomplete tasks carry forward with adjusted priority

**AWS Dependencies:** Amazon EventBridge Scheduler, AWS Lambda, Amazon SNS, Amazon SES

---

### 3.4 Job Description Mapping — `P0`

**As a** student,  
**I want to** understand how job requirements map to my preparation,  
**So that** I can focus on skills that matter for my target role.

**Acceptance Criteria:**
- 3.4.1 System analyzes job descriptions for target roles and companies using NLP extraction
- 3.4.2 System extracts required skills, technologies, experience levels, and interview patterns
- 3.4.3 System maps extracted requirements to specific learning modules in the roadmap
- 3.4.4 System shows a visual skill-gap matrix: current level vs. required level per skill
- 3.4.5 System refreshes job market data weekly from integrated job boards
- 3.4.6 Students can paste custom job descriptions for instant analysis and plan adjustment

**AWS Dependencies:** Amazon Bedrock (NLP extraction), Amazon Comprehend, Amazon S3 (JD storage), AWS Lambda

---

### 3.5 Multi-Language Support — `P0`

**As a** non-English speaking student,  
**I want to** access content in my preferred language,  
**So that** I can understand technical concepts more effectively.

**Acceptance Criteria:**
- 3.5.1 System provides UI and content in: English, Hindi, Tamil, Telugu, Bengali, Marathi
- 3.5.2 Technical concepts include language-appropriate real-world examples and analogies
- 3.5.3 Code explanations, error messages, and debugging walkthroughs available in preferred language
- 3.5.4 Interview preparation materials (behavioral questions, HR round prep) support all languages
- 3.5.5 Technical terms (e.g., "binary tree", "API") remain in English with vernacular explanations
- 3.5.6 Students can switch display language at any time without losing progress
- 3.5.7 Translation quality validated against a curated technical glossary per language

**AWS Dependencies:** Amazon Translate, Amazon Bedrock (contextual explanation), Amazon S3 (glossaries)

---

### 3.6 Progress Tracking & Analytics — `P0`

**As a** student,  
**I want to** track my progress and see how I'm improving,  
**So that** I stay motivated and understand my readiness level.

**Acceptance Criteria:**
- 3.6.1 System tracks completion of daily tasks, weekly milestones, and overall roadmap progress
- 3.6.2 Dashboard shows progress visualizations: skill radar chart, completion timeline, streak counter
- 3.6.3 System computes a composite readiness score (0–100) based on: technical skills, problem-solving, system design, behavioral prep, domain knowledge
- 3.6.4 Analytics display: time spent per skill, topics covered, problems solved, accuracy rates
- 3.6.5 System identifies the top 3 weakest areas and surfaces them as priority recommendations
- 3.6.6 Progress reports exportable as PDF, shareable via link with mentors or peers
- 3.6.7 Weekly summary email with key stats and motivational nudges

**AWS Dependencies:** Amazon QuickSight (admin analytics), Amazon RDS (metrics), Amazon SES (reports), Amazon CloudWatch (custom metrics)

---

### 3.7 Interview Simulation — `P1`

**As a** student,  
**I want to** practice interviews aligned with my target role,  
**So that** I can build confidence and identify areas for improvement.

**Acceptance Criteria:**
- 3.7.1 System provides role-specific questions: DSA coding, system design, behavioral, domain-specific
- 3.7.2 Mock interviews simulate real company formats (e.g., Amazon Leadership Principles, Google system design rounds)
- 3.7.3 AI provides detailed feedback on answers: correctness, approach, time complexity, communication
- 3.7.4 Question difficulty adapts: increases after >80% success rate, decreases after <40%
- 3.7.5 System tracks interview performance trends over time with improvement suggestions
- 3.7.6 Students can practice in preferred language (questions + feedback)
- 3.7.7 Timed sessions with configurable duration (30/45/60 minutes)

**AWS Dependencies:** Amazon Bedrock (AI interviewer), Amazon DynamoDB (question bank), AWS Lambda (evaluation)

---

### 3.8 Skill Reinforcement — `P1`

**As a** student,  
**I want to** regularly review and reinforce learned concepts,  
**So that** I retain knowledge and build long-term competency.

**Acceptance Criteria:**
- 3.8.1 System schedules periodic reviews using spaced repetition (SM-2 algorithm variant)
- 3.8.2 Review intervals adapt based on recall accuracy: correct → longer interval, incorrect → shorter
- 3.8.3 Quick quizzes (5–10 questions, 5–10 minutes) reinforce key concepts per topic
- 3.8.4 System identifies concepts with declining retention and auto-schedules remediation
- 3.8.5 Reinforcement activities are integrated into daily plans as "review" task type
- 3.8.6 Students can manually trigger on-demand review for any previously completed topic

**AWS Dependencies:** Amazon DynamoDB (spaced repetition state), AWS Lambda (scheduling)

---

### 3.9 Resource Curation — `P1`

**As a** student,  
**I want to** access curated, high-quality learning resources,  
**So that** I don't waste time searching for materials.

**Acceptance Criteria:**
- 3.9.1 System recommends resources (courses, tutorials, articles, videos) based on current learning phase and skill level
- 3.9.2 Resources filtered and ranked by: quality score, relevance, language, difficulty, user ratings
- 3.9.3 System includes both free and paid options with clear labeling
- 3.9.4 Coding problems sourced/linked from LeetCode, HackerRank, Codeforces, GeeksForGeeks
- 3.9.5 Resources tagged to specific job requirements and learning modules
- 3.9.6 Students can bookmark, rate, and annotate resources
- 3.9.7 Resource library updated monthly; stale resources flagged and reviewed

**AWS Dependencies:** Amazon OpenSearch (full-text search), Amazon S3 (resource metadata), AWS Lambda (curation pipeline)

---

### 3.10 Adaptive Learning Path — `P1`

**As a** student,  
**I want to** have my learning path adjust based on my performance,  
**So that** I'm always challenged appropriately and don't get stuck.

**Acceptance Criteria:**
- 3.10.1 System continuously monitors: task completion rate, quiz scores, time-per-task, streak patterns
- 3.10.2 If completion rate <50% for 3+ consecutive days → auto-reduce daily task load by 20%
- 3.10.3 System provides additional explainers and easier problems for struggling areas
- 3.10.4 If completion rate >90% for 5+ consecutive days → offer accelerated path or advanced challenges
- 3.10.5 System suggests alternative learning approaches (video vs. text, project-based vs. theory) when progress stalls for 7+ days
- 3.10.6 All adaptations happen automatically; student is notified of changes with rationale
- 3.10.7 Student can override or revert automatic adjustments

**AWS Dependencies:** Amazon SageMaker (adaptive model), Amazon EventBridge (triggers), Amazon SNS (notifications)

---

### 3.11 Gamification & Motivation — `P2`

**As a** student,  
**I want to** earn rewards and see my achievements,  
**So that** I stay motivated throughout the preparation journey.

**Acceptance Criteria:**
- 3.11.1 System awards badges for milestones (e.g., "7-Day Streak", "100 Problems Solved", "First Mock Interview")
- 3.11.2 XP-based leveling system reflecting overall progress
- 3.11.3 Opt-in leaderboards for college-level and role-level comparisons
- 3.11.4 Daily streaks with visual indicators and gentle nudges for broken streaks
- 3.11.5 Achievement sharing to social media / LinkedIn

**AWS Dependencies:** Amazon DynamoDB (gamification state), Amazon S3 (badge assets)

---

### 3.12 Offline Mode — `P2`

**As a** student with limited internet access,  
**I want to** download content for offline use,  
**So that** I can continue learning without connectivity.

**Acceptance Criteria:**
- 3.12.1 Daily plan and associated reading materials downloadable as offline bundle
- 3.12.2 Offline progress syncs automatically when connectivity resumes
- 3.12.3 Downloaded content expires after 7 days to ensure freshness
- 3.12.4 Offline mode supports text content and cached quiz data (not video streaming)

**AWS Dependencies:** Amazon CloudFront (content delivery), Service Worker (PWA)

---

## 4. Non-Functional Requirements

### 4.1 Performance

| Metric | Target | AWS Service |
|--------|--------|-------------|
| Roadmap generation latency | < 30 seconds | Amazon Bedrock / SageMaker |
| Daily plan generation | < 5 seconds | AWS Lambda |
| API response time (p95) | < 500ms | API Gateway + Lambda |
| Page load time (p95) | < 2 seconds | Amazon CloudFront |
| Concurrent users | 10,000+ | Auto Scaling + ALB |
| Daily plan availability | By midnight (user TZ) | EventBridge Scheduler |

### 4.2 Scalability
- Serverless-first architecture (AWS Lambda, API Gateway) scales to millions of requests
- Amazon Aurora Serverless v2 auto-scales database capacity on demand
- Amazon DynamoDB on-demand mode for unpredictable traffic patterns
- Amazon S3 for unlimited content storage
- Multi-AZ deployment for high availability

### 4.3 Accessibility
- Mobile-responsive PWA design for smartphone access (70%+ users expected on mobile)
- Optimized for low-bandwidth (2G/3G): compressed assets, lazy loading, < 500KB initial bundle
- Offline mode via Service Worker for downloaded content
- WCAG 2.1 AA compliant: screen reader support, keyboard navigation, color contrast ratios
- RTL layout support planned for Phase 2 (Urdu)

### 4.4 Security & Privacy
- **Authentication:** Amazon Cognito with MFA support
- **Authorization:** IAM-based roles (student, admin, content-manager)
- **Encryption at rest:** AWS KMS (AES-256) for RDS, S3, DynamoDB
- **Encryption in transit:** TLS 1.3 enforced via CloudFront + ALB
- **Compliance:** India's DPDP Act 2023, GDPR for international users
- **Data residency:** Primary region `ap-south-1` (Mumbai)
- **Privacy:** No PII sharing without explicit consent; anonymized analytics
- **Protection:** AWS WAF for DDoS protection and bot mitigation
- **Auditing:** Quarterly security audits and penetration testing

### 4.5 Reliability
- **Uptime SLA:** 99.9% (target 99.95%)
- **Multi-AZ:** Deployed across `ap-south-1a`, `ap-south-1b`, `ap-south-1c`
- **Backups:** RDS automated snapshots (35-day retention), DynamoDB Point-in-Time Recovery
- **Degradation:** Cached responses served when AI services unavailable
- **Error handling:** Dead letter queues (SQS DLQ), circuit breaker for external APIs
- **Recovery:** RTO < 1 hour, RPO < 5 minutes

### 4.6 Usability
- Intuitive interface requiring < 5 minutes onboarding
- Breadcrumb navigation and progress indicators throughout
- Guided onboarding flow with contextual tooltips
- Mobile-first design with touch-optimized interactions
- Maximum 3 clicks to any core feature from dashboard

### 4.7 Observability
- Centralized logging via Amazon CloudWatch Logs
- Distributed tracing via AWS X-Ray
- Custom CloudWatch dashboards for system health
- Alerting via CloudWatch Alarms → Amazon SNS
- Structured error codes with correlation IDs

---

## 5. Technical Constraints

| Constraint | Detail |
|-----------|--------|
| Cloud Provider | **AWS only** — all infrastructure on Amazon Web Services |
| Primary Region | `ap-south-1` (Mumbai) for low-latency India access |
| DR Region | `ap-southeast-1` (Singapore) for disaster recovery |
| AI/ML Platform | Amazon Bedrock (Claude/Titan) + Amazon SageMaker for custom models |
| Authentication | Amazon Cognito — no third-party auth providers |
| Infrastructure as Code | AWS CDK (TypeScript) or Terraform |
| CI/CD | AWS CodePipeline + CodeBuild + CodeDeploy |
| Compute | AWS Lambda (serverless) + Amazon ECS Fargate (containers) |
| Coding Platform Integration | REST API with LeetCode, HackerRank, GeeksForGeeks |
| Job Board Integration | LinkedIn Jobs, Naukri, Indeed (API / scraping) |
| Mobile Strategy | PWA first (Phase 1); React Native (Phase 2) |
| Language/NLP | Amazon Translate + Amazon Comprehend + Bedrock |
| Budget | Target < $5,000/month at 10K MAU; optimize Free Tier |

---

## 6. Integration Requirements

### 6.1 External Platforms

| Platform | Integration Type | Purpose |
|----------|-----------------|---------|
| LeetCode | API / Web Scraping | Coding problem links, difficulty mapping |
| HackerRank | API | Skill assessments, coding challenges |
| GeeksForGeeks | Web Scraping | Tutorial and problem references |
| LinkedIn Jobs | API / Scraping | Job description analysis, market trends |
| Naukri.com | API | India-specific job market data |
| YouTube | Data API v3 | Video tutorial recommendations |
| GitHub | OAuth + API | Portfolio integration, project tracking |

### 6.2 AWS Service Map

| Service | Purpose |
|---------|---------|
| Amazon Cognito | User authentication & authorization |
| Amazon API Gateway | REST API management, throttling, API keys |
| AWS Lambda | Serverless compute for business logic |
| Amazon ECS Fargate | Containerized AI/ML inference services |
| Amazon RDS Aurora (PostgreSQL) | Primary relational database |
| Amazon DynamoDB | NoSQL for roadmaps, daily plans, sessions |
| Amazon ElastiCache (Redis) | Caching, session store, rate limiting |
| Amazon S3 | Static assets, content storage, backups |
| Amazon CloudFront | Global CDN |
| Amazon Bedrock | Generative AI (roadmap, interview, explanations) |
| Amazon SageMaker | Custom ML models (assessment, adaptive learning) |
| Amazon Translate | Multi-language translation |
| Amazon Comprehend | NLP for job description analysis |
| Amazon SES | Transactional emails |
| Amazon SNS | Push notifications, alerts |
| Amazon SQS | Async message queuing |
| Amazon EventBridge | Event-driven scheduling |
| AWS Step Functions | Multi-step workflow orchestration |
| Amazon OpenSearch | Full-text resource search |
| Amazon QuickSight | Admin analytics dashboards |
| AWS CloudWatch | Monitoring, logging, alerting |
| AWS X-Ray | Distributed tracing |
| AWS WAF | Web application firewall |
| AWS KMS | Encryption key management |
| AWS CodePipeline | CI/CD pipeline |
| AWS CDK | Infrastructure as Code |

---

## 7. Success Metrics

### 7.1 Engagement

| Metric | Target (6 months) |
|--------|-------------------|
| Daily Active Users (DAU) | 70% of registered users |
| Task Completion Rate | > 60% daily |
| Avg Session Duration | > 25 minutes |
| 7-Day Retention | > 50% |
| 30-Day Retention | > 30% |

### 7.2 Learning Outcomes

| Metric | Target |
|--------|--------|
| Readiness Score Improvement | +30 points in 60 days |
| Skill Gap Closure | 70% of identified gaps |
| Problems Solved (avg/student) | 200+ |
| Mock Interview Score (at completion) | 70%+ |

### 7.3 Placement

| Metric | Target |
|--------|--------|
| Interview Conversion Rate | > 40% |
| Job Offer Rate (roadmap completers) | > 25% |
| Time to Job-Ready | < 90 days |

### 7.4 Platform Health

| Metric | Target |
|--------|--------|
| API Latency (p95) | < 500ms |
| Uptime | 99.9%+ |
| NPS Score | > 50 |
| Translation Accuracy | > 90% |
| Cost per MAU | < ₹40 (~$0.50) |

---

## 8. Assumptions & Dependencies

### 8.1 Assumptions
- Students have access to a smartphone or computer with internet (at least 2G)
- Students can create an email account for registration
- Job market data from public sources (job boards) is sufficient for JD analysis
- Amazon Bedrock models support Indic language generation with acceptable quality
- Initial content library (resources, problems, tutorials) will be manually curated before launch

### 8.2 Dependencies
- Amazon Bedrock availability in `ap-south-1` region
- Amazon Translate quality for technical Indic language content
- Third-party API stability (LeetCode, HackerRank, LinkedIn)
- Content licensing for recommended paid resources
- Domain expertise for initial skill-to-role mapping and prerequisite graphs

---

## 9. Glossary

| Term | Definition |
|------|-----------|
| **Roadmap** | A personalized, ordered sequence of learning milestones and modules tailored to a student's goals |
| **Daily Plan** | A set of time-bound tasks generated each day from the active roadmap |
| **Readiness Score** | A composite score (0–100) indicating how prepared a student is for their target role |
| **Skill Gap** | The delta between a student's current skill level and the level required by the target role |
| **Milestone** | A major checkpoint in the roadmap representing mastery of a skill cluster |
| **Learning Module** | A focused unit of study within a milestone covering a specific topic or skill |
| **Spaced Repetition** | An evidence-based review technique that schedules reviews at increasing intervals |
| **Adaptive Learning** | Dynamic difficulty/pacing adjustment based on student performance patterns |
| **JD Mapping** | Extracting structured skill requirements from unstructured job descriptions |

---

## 10. Out of Scope (Phase 1)

- Direct job application submission through the platform
- Employer-facing dashboards and analytics
- Peer-to-peer mentoring or community features
- Live instructor-led classes or webinars
- Resume/CV building and review tools
- Salary negotiation guidance
- Native mobile apps (iOS/Android) — PWA only in Phase 1
- Video content hosting (links to external sources only)
- Payment processing for premium features
