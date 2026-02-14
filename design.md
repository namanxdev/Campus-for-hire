# Design: Campus-to-Hire Personalization Platform

## 1. System Overview

The Campus-to-Hire Personalization Platform is an AI-driven, cloud-native system built entirely on **AWS** that transforms generic career preparation into personalized, goal-aligned learning experiences. The platform analyzes student profiles, job market requirements, and learning patterns to generate adaptive roadmaps with daily actionable tasks — all served through a serverless-first architecture optimized for cost, scale, and low-latency access from India.

---

## 2. AWS Architecture

### 2.1 High-Level Architecture Diagram

```
┌──────────────────────────────────────────────────────────────────────────┐
│                         CLIENT LAYER                                     │
│   React/Next.js PWA  ──→  Amazon CloudFront (CDN)  ──→  Amazon S3       │
│   (Mobile-Responsive)      + AWS WAF                    (Static Hosting) │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │ HTTPS (TLS 1.3)
┌──────────────────────────────────▼───────────────────────────────────────┐
│                        API LAYER                                         │
│   Amazon API Gateway (REST)                                              │
│   ├── Amazon Cognito Authorizer (JWT validation)                        │
│   ├── Rate Limiting & Throttling                                        │
│   ├── Request Validation                                                │
│   └── Usage Plans & API Keys                                            │
└──────────────────────────────────┬───────────────────────────────────────┘
                                   │
          ┌────────────────────────┼────────────────────────┐
          │                        │                        │
┌─────────▼──────────┐  ┌─────────▼──────────┐  ┌─────────▼──────────┐
│  COMPUTE LAYER     │  │   AI/ML LAYER      │  │  ASYNC LAYER       │
│                    │  │                    │  │                    │
│  AWS Lambda        │  │  Amazon Bedrock    │  │  Amazon SQS        │
│  (Node.js 20.x)   │  │  (Claude 3.5/      │  │  Amazon EventBridge│
│  ├─ Profile API    │  │   Titan)           │  │  AWS Step Functions│
│  ├─ Roadmap API    │  │  ├─ Roadmap Gen    │  │  ├─ Daily Plan Gen │
│  ├─ Daily Plan API │  │  ├─ Interview AI   │  │  ├─ JD Scraping    │
│  ├─ Progress API   │  │  ├─ Content Explain│  │  ├─ Notifications  │
│  ├─ Interview API  │  │  └─ JD Analysis    │  │  └─ Analytics Agg  │
│  └─ Resource API   │  │                    │  │                    │
│                    │  │  Amazon SageMaker   │  │  Amazon SNS        │
│  Amazon ECS        │  │  ├─ Skill Assess   │  │  (Push Notifs)     │
│  Fargate           │  │  ├─ Adaptive Learn │  │                    │
│  (Long-running ML) │  │  └─ Recommendation │  │  Amazon SES        │
│                    │  │                    │  │  (Email)           │
│                    │  │  Amazon Translate   │  │                    │
│                    │  │  Amazon Comprehend  │  │                    │
└─────────┬──────────┘  └─────────┬──────────┘  └─────────┬──────────┘
          │                        │                        │
          └────────────────────────┼────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                         DATA LAYER                                       │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────────────┐  │
│  │ Amazon RDS      │  │ Amazon DynamoDB │  │ Amazon ElastiCache     │  │
│  │ Aurora Postgres  │  │                 │  │ (Redis)                │  │
│  │ Serverless v2   │  │ ├─ Roadmaps     │  │ ├─ Session Cache       │  │
│  │                 │  │ ├─ Daily Plans   │  │ ├─ Daily Plan Cache    │  │
│  │ ├─ Students     │  │ ├─ Tasks        │  │ ├─ Translation Cache   │  │
│  │ ├─ Skills       │  │ ├─ Interview Q  │  │ └─ Rate Limit Counters │  │
│  │ ├─ Progress     │  │ ├─ Gamification │  │                         │  │
│  │ └─ Resources    │  │ └─ Spaced Rep   │  └─────────────────────────┘  │
│  └─────────────────┘  └─────────────────┘                                │
│                                                                          │
│  ┌─────────────────┐  ┌─────────────────┐                               │
│  │ Amazon S3       │  │ Amazon          │                               │
│  │ ├─ Static Assets│  │ OpenSearch      │                               │
│  │ ├─ JD Documents │  │ Serverless      │                               │
│  │ ├─ Glossaries   │  │ (Resource       │                               │
│  │ ├─ Exports/PDF  │  │  Full-Text      │                               │
│  │ └─ Backups      │  │  Search)        │                               │
│  └─────────────────┘  └─────────────────┘                               │
└──────────────────────────────────────────────────────────────────────────┘
                                   │
┌──────────────────────────────────▼───────────────────────────────────────┐
│                      OBSERVABILITY LAYER                                 │
│  Amazon CloudWatch (Logs + Metrics + Alarms)                            │
│  AWS X-Ray (Distributed Tracing)                                        │
│  Amazon QuickSight (Admin/BI Dashboards)                                │
└──────────────────────────────────────────────────────────────────────────┘
```

### 2.2 Network Architecture

```
AWS Region: ap-south-1 (Mumbai)
├── VPC: 10.0.0.0/16
│   ├── Public Subnets (3 AZs)
│   │   ├── 10.0.1.0/24 (ap-south-1a) — NAT Gateway, ALB
│   │   ├── 10.0.2.0/24 (ap-south-1b) — NAT Gateway
│   │   └── 10.0.3.0/24 (ap-south-1c) — NAT Gateway
│   ├── Private Subnets - Application (3 AZs)
│   │   ├── 10.0.10.0/24 (ap-south-1a) — Lambda, ECS Fargate
│   │   ├── 10.0.11.0/24 (ap-south-1b) — Lambda, ECS Fargate
│   │   └── 10.0.12.0/24 (ap-south-1c) — Lambda, ECS Fargate
│   └── Private Subnets - Data (3 AZs)
│       ├── 10.0.20.0/24 (ap-south-1a) — RDS, ElastiCache
│       ├── 10.0.21.0/24 (ap-south-1b) — RDS, ElastiCache
│       └── 10.0.22.0/24 (ap-south-1c) — RDS, ElastiCache
│
├── VPC Endpoints (Private Link)
│   ├── S3 Gateway Endpoint
│   ├── DynamoDB Gateway Endpoint
│   ├── SQS Interface Endpoint
│   ├── Bedrock Interface Endpoint
│   ├── SageMaker Interface Endpoint
│   └── Secrets Manager Interface Endpoint
│
DR Region: ap-southeast-1 (Singapore)
├── Cross-region RDS read replica
├── S3 cross-region replication
└── CloudFront failover origin
```

---

## 3. Component Design

### 3.1 Student Profile Service

**AWS Services:** AWS Lambda (Node.js 20.x), Amazon Cognito, Amazon RDS Aurora PostgreSQL

**Purpose:** Manages student profiles, authentication, assessments, and preferences.

**Key Components:**
- **Auth Manager** (Cognito): Registration, login, MFA, password reset, social sign-in
- **Profile Manager** (Lambda → RDS): CRUD operations for student data
- **Skill Assessor** (Lambda → Bedrock + RDS): Initial and ongoing skill evaluation
- **Preference Handler** (Lambda → RDS): Language, time, and goal preferences

**Data Model:**
```typescript
interface StudentProfile {
  id: string;                    // UUID, PK
  cognitoSub: string;           // Cognito User Pool sub
  personalInfo: {
    name: string;
    email: string;               // unique, from Cognito
    phone?: string;
    college: string;
    collegeTier: 'tier1' | 'tier2' | 'tier3';
    graduationYear: number;
    state: string;               // Indian state for regional context
  };
  background: {
    degree: string;              // B.Tech, BCA, MCA, etc.
    major: string;               // CS, ECE, Mechanical, etc.
    isCSBackground: boolean;
    currentYear: number;         // 1-4
    cgpa?: number;
    internships: number;
    projectCount: number;
  };
  skills: SkillAssessment[];
  goals: {
    targetRole: TargetRole;
    targetCompanies: string[];   // max 5
    desiredStartDate: Date;
    dreamCompany?: string;
  };
  availability: {
    hoursPerDay: number;         // 1-12
    daysPerWeek: number;         // 1-7
    preferredTimeSlots: TimeSlot[];
    timezone: string;            // IANA timezone
  };
  preferences: {
    primaryLanguage: SupportedLanguage;
    secondaryLanguages: SupportedLanguage[];
    learningStyle: 'visual' | 'reading' | 'practice' | 'mixed';
    notificationPreferences: {
      email: boolean;
      push: boolean;
      sms: boolean;
      dailyReminderTime: string; // HH:mm
    };
  };
  onboardingCompleted: boolean;
  createdAt: Date;
  updatedAt: Date;
}

type TargetRole = 'sde' | 'cloud_engineer' | 'data_analyst' | 'devops' 
  | 'qa' | 'ml_engineer' | 'fullstack_developer';

type SupportedLanguage = 'en' | 'hi' | 'ta' | 'te' | 'bn' | 'mr';

type TimeSlot = 'early_morning' | 'morning' | 'afternoon' | 'evening' | 'night';

interface SkillAssessment {
  skillId: string;
  skillName: string;
  category: 'dsa' | 'programming' | 'system_design' | 'database' | 'cloud' 
    | 'os' | 'networking' | 'behavioral' | 'domain_specific';
  level: 'beginner' | 'intermediate' | 'advanced';
  score: number;                 // 0-100
  assessedVia: 'self' | 'quiz' | 'coding_challenge' | 'adaptive';
  lastAssessed: Date;
  confidenceScore: number;       // 0-1, system confidence in assessment
}
```

**API Endpoints:**
| Method | Endpoint | Lambda | Description |
|--------|----------|--------|-------------|
| POST | `/api/auth/register` | `auth-register` | Register via Cognito |
| POST | `/api/auth/login` | `auth-login` | Login, return JWT |
| POST | `/api/auth/refresh` | `auth-refresh` | Refresh access token |
| POST | `/api/auth/forgot-password` | `auth-forgot` | Initiate password reset |
| GET | `/api/profile` | `profile-get` | Get student profile |
| PUT | `/api/profile` | `profile-update` | Update profile |
| POST | `/api/profile/assessment` | `profile-assess` | Submit skill assessment |
| GET | `/api/profile/skills` | `profile-skills` | Get current skill levels |
| PUT | `/api/profile/preferences` | `profile-prefs` | Update preferences |

---

### 3.2 Roadmap Generation Service

**AWS Services:** AWS Lambda, Amazon Bedrock (Claude 3.5 Sonnet), Amazon DynamoDB, AWS Step Functions, Amazon SQS

**Purpose:** Creates personalized learning roadmaps using generative AI with rule-based constraints.

**Key Components:**
- **Job Analyzer** (Lambda + Bedrock + Comprehend): Analyzes JDs, extracts skill requirements
- **Skill Gap Identifier** (Lambda): Compares current vs. required skills with weighted scoring
- **Path Generator** (Step Functions + Bedrock): Creates prerequisite-ordered learning paths
- **Timeline Optimizer** (Lambda): Adjusts milestones based on student availability

**Roadmap Generation Flow (AWS Step Functions):**

```
┌─────────────────────┐
│  Trigger: API Call   │
│  POST /api/roadmap/  │
│  generate            │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 1: Validate    │   Lambda: roadmap-validate
│  Profile & Goals     │   Input: studentId
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 2: Fetch Job   │   Lambda: roadmap-fetch-jd
│  Requirements        │   Source: DynamoDB JD cache
│  (Parallel)          │   + Bedrock for analysis
│  ├─ Target Role      │
│  └─ Target Companies │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 3: Compute     │   Lambda: roadmap-skill-gap
│  Skill Gaps          │   Compare: current vs required
│  (Weighted Scoring)  │   Output: prioritized gap list
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 4: Generate    │   Lambda: roadmap-generate
│  Learning Path       │   Bedrock: Claude 3.5 Sonnet
│  (AI + Rule Engine)  │   Rules: prerequisite DAG
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 5: Optimize    │   Lambda: roadmap-optimize
│  Timeline            │   Input: availability config
│  (Fit to schedule)   │   Output: milestone dates
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 6: Generate    │   Lambda: roadmap-alternatives
│  Alternative Paths   │   Output: standard + accelerated
│  (Min 2 options)     │
└──────────┬──────────┘
           ▼
┌─────────────────────┐
│  Step 7: Store &     │   DynamoDB: roadmaps table
│  Return Roadmap      │   SNS: notify student
└─────────────────────┘
```

**Bedrock Prompt Strategy:**
```
System: You are an expert career coach specializing in tech placements.
Given a student profile and skill gaps, generate a structured learning 
roadmap with milestones, modules, and resource suggestions.

Rules:
- Respect prerequisite ordering (provided DAG)
- Each milestone: 1-3 weeks duration
- Each module: 2-10 hours
- Balance theory (30%), practice (50%), interview prep (20%)
- Prioritize highest-weight skill gaps first

Input: {studentProfile}, {skillGaps}, {jobRequirements}, {availableTime}
Output: JSON roadmap with milestones[], modules[], timeline
```

**Data Model:**
```typescript
// Stored in DynamoDB — partition key: studentId, sort key: roadmapId
interface Roadmap {
  roadmapId: string;              // UUID
  studentId: string;              // FK
  version: number;                // for roadmap revisions
  targetRole: TargetRole;
  targetCompanies: string[];
  generatedAt: Date;
  generatedBy: 'bedrock-claude3.5' | 'rule-engine';
  estimatedDurationDays: number;
  totalEstimatedHours: number;
  milestones: Milestone[];
  skillGaps: SkillGap[];
  alternativePaths: AlternativePath[];
  status: 'draft' | 'active' | 'completed' | 'paused' | 'superseded';
  completionPercentage: number;
  lastUpdated: Date;
  metadata: {
    bedrockModelId: string;
    bedrockRequestId: string;
    generationLatencyMs: number;
    promptTokens: number;
    completionTokens: number;
  };
}

interface Milestone {
  milestoneId: string;
  title: string;
  description: string;
  order: number;                  // sequential position
  skillCluster: string[];         // skills covered
  modules: LearningModule[];
  estimatedDays: number;
  startDate?: Date;
  targetDate?: Date;
  completionCriteria: string[];
  status: 'not_started' | 'in_progress' | 'completed';
  completedAt?: Date;
  prerequisites: string[];        // other milestoneIds
}

interface LearningModule {
  moduleId: string;
  title: string;
  type: 'theory' | 'practice' | 'project' | 'interview_prep' | 'review';
  skills: string[];
  topics: string[];
  resources: ResourceRef[];
  estimatedHours: number;
  difficulty: 'easy' | 'medium' | 'hard';
  order: number;
  completionCriteria: string;
  status: 'not_started' | 'in_progress' | 'completed';
}

interface SkillGap {
  skillId: string;
  skillName: string;
  currentLevel: number;           // 0-100
  requiredLevel: number;          // 0-100
  gapScore: number;               // weighted priority
  priority: 'critical' | 'high' | 'medium' | 'low';
  coveredByModules: string[];     // moduleIds
}

interface AlternativePath {
  pathType: 'standard' | 'accelerated' | 'deep_dive';
  estimatedDays: number;
  description: string;
  milestoneAdjustments: {
    milestoneId: string;
    adjustedDays: number;
    adjustedModules: string[];
  }[];
}

interface ResourceRef {
  resourceId: string;
  title: string;
  type: 'video' | 'article' | 'problem' | 'documentation' | 'project';
  url: string;
  provider: string;
  isPrimary: boolean;             // main resource vs. supplementary
}
```

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/roadmap/generate` | Trigger roadmap generation (async — returns Step Functions execution ARN) |
| GET | `/api/roadmap/generate/status/:executionId` | Poll generation status |
| GET | `/api/roadmap` | Get active roadmap |
| GET | `/api/roadmap/:roadmapId` | Get specific roadmap |
| PUT | `/api/roadmap/activate` | Activate a draft roadmap |
| PUT | `/api/roadmap/pause` | Pause active roadmap |
| POST | `/api/roadmap/regenerate` | Request new roadmap (supersedes current) |
| GET | `/api/roadmap/milestones` | Get milestones with status |
| GET | `/api/roadmap/skill-gaps` | Get current skill gap analysis |

---

### 3.3 Daily Plan Generator

**AWS Services:** AWS Lambda, Amazon EventBridge Scheduler, Amazon DynamoDB, Amazon SQS, Amazon SNS, Amazon SES

**Purpose:** Breaks down roadmap into daily actionable tasks, generated automatically each night.

**Generation Architecture:**

```
Amazon EventBridge Scheduler
  │  (Cron: midnight per timezone batch)
  ▼
AWS Lambda: daily-plan-trigger
  │  (Queries students by timezone → pushes to SQS)
  ▼
Amazon SQS: daily-plan-queue
  │  (Batch size: 10, concurrency: 50)
  ▼
AWS Lambda: daily-plan-generate
  │  (Per student: fetch roadmap → generate tasks → store)
  ▼
Amazon DynamoDB: daily-plans table
  │
  ├──→ Amazon SNS: Push notification ("Your daily plan is ready!")
  └──→ Amazon SES: Email with daily summary
```

**Task Generation Algorithm:**
```
Input: student.availability, roadmap.currentMilestone, student.progressHistory
Output: DailyPlan with balanced tasks

1. Get available hours for today (from availability config)
2. Get current milestone and in-progress modules
3. Calculate remaining capacity per module
4. Select tasks from:
   a. Spaced repetition reviews (priority: HIGH if overdue)
   b. Current module learning tasks (priority: based on milestone deadline)
   c. Coding practice problems (difficulty: adaptive from performance)
   d. Interview practice (if milestone includes it)
5. Balance by type:
   - ≥ 1 theory/learning task
   - ≥ 1 practice/coding task
   - 1 review task (if available)
   - Total time ≤ available hours
6. Carry forward incomplete tasks from yesterday (boost priority)
7. Assign time estimates (15, 30, 45, 60 min blocks)
8. Store plan in DynamoDB
9. Schedule notifications
```

**Data Model:**
```typescript
// DynamoDB — PK: studentId, SK: date (YYYY-MM-DD)
interface DailyPlan {
  studentId: string;
  date: string;                   // YYYY-MM-DD
  timezone: string;
  totalEstimatedMinutes: number;
  availableMinutes: number;
  tasks: Task[];
  carryForwardCount: number;      // tasks from previous days
  status: 'generated' | 'in_progress' | 'completed' | 'partial';
  completionRate: number;         // 0-100
  generatedAt: Date;
  generatedBy: 'scheduler' | 'manual_refresh';
}

interface Task {
  taskId: string;
  title: string;
  description: string;
  type: 'learn' | 'practice' | 'review' | 'interview' | 'project' | 'quiz';
  moduleId: string;
  milestoneId: string;
  estimatedMinutes: number;       // 15, 30, 45, or 60
  priority: 'critical' | 'high' | 'medium' | 'low';
  resources: ResourceRef[];
  completionCriteria: string;
  isCarryForward: boolean;
  isSpacedRepetition: boolean;
  status: 'not_started' | 'in_progress' | 'completed' | 'skipped';
  startedAt?: Date;
  completedAt?: Date;
  skipReason?: string;
  actualMinutes?: number;         // self-reported time spent
}
```

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/daily-plan` | Get today's plan |
| GET | `/api/daily-plan/:date` | Get plan for specific date |
| POST | `/api/daily-plan/refresh` | Manually regenerate today's plan |
| PATCH | `/api/daily-plan/task/:taskId` | Update task status (complete/skip/start) |
| GET | `/api/daily-plan/history?from=&to=` | Get plans for date range |

---

### 3.4 Progress Tracking Service

**AWS Services:** AWS Lambda, Amazon RDS Aurora, Amazon CloudWatch (custom metrics), Amazon SES, Amazon S3

**Purpose:** Monitors student progress, computes readiness scores, and provides analytics.

**Key Components:**
- **Activity Logger** (Lambda): Records task completions, time spent, scores
- **Analytics Engine** (Lambda + RDS): Computes daily/weekly/monthly aggregates
- **Readiness Calculator** (Lambda): Composite scoring model
- **Report Generator** (Lambda + S3): PDF reports, shareable links

**Readiness Score Formula:**
```
ReadinessScore = Σ(weight_i × skill_score_i) / Σ(weight_i)

Where weights are derived from target role requirements:
  SDE:  DSA(30%) + SystemDesign(20%) + Programming(25%) + Behavioral(15%) + OS/DB(10%)
  Cloud: Cloud(35%) + Networking(20%) + DevOps(15%) + Programming(15%) + Security(15%)
  ...

skill_score_i = f(assessment_score, problems_solved, quiz_accuracy, interview_performance)
```

**Data Model:**
```typescript
// RDS Aurora PostgreSQL
interface ProgressRecord {
  id: string;
  studentId: string;
  date: string;                   // YYYY-MM-DD
  // Daily metrics
  tasksCompleted: number;
  tasksTotal: number;
  tasksSkipped: number;
  minutesSpent: number;
  minutesEstimated: number;
  // Performance
  problemsSolved: number;
  problemsAttempted: number;
  avgProblemAccuracy: number;     // 0-100
  quizScore: number;              // 0-100
  interviewsPracticed: number;
  interviewAvgScore: number;
  // Engagement
  loginStreak: number;
  sessionCount: number;
  // Computed
  readinessScore: number;         // 0-100
  dayOverDayDelta: number;        // readiness change
  completionRate: number;         // tasks completed / total
}

interface ReadinessScore {
  studentId: string;
  computedAt: Date;
  overall: number;                // 0-100
  breakdown: {
    technicalSkills: number;
    problemSolving: number;
    systemDesign: number;
    behavioralPrep: number;
    domainKnowledge: number;
  };
  roleAlignment: number;          // % match with target role
  companyAlignment: Record<string, number>; // per target company
  trend: 'improving' | 'stable' | 'declining';
  topGaps: string[];              // top 3 weakest areas
  recommendations: string[];
  nextMilestoneETA: Date;
}

interface WeeklyReport {
  studentId: string;
  weekStartDate: string;
  weekEndDate: string;
  summary: {
    tasksCompleted: number;
    totalMinutes: number;
    problemsSolved: number;
    readinessChange: number;
    streakDays: number;
    topAchievement: string;
  };
  skillProgress: {
    skill: string;
    startLevel: number;
    endLevel: number;
    delta: number;
  }[];
  focusAreasNextWeek: string[];
  reportUrl: string;              // S3 pre-signed URL for PDF
}
```

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/progress/dashboard` | Aggregated dashboard data |
| GET | `/api/progress/readiness` | Current readiness score + breakdown |
| GET | `/api/progress/analytics?period=week\|month\|all` | Detailed analytics |
| GET | `/api/progress/history?from=&to=` | Historical progress records |
| GET | `/api/progress/report/weekly` | Generate & return weekly report |
| POST | `/api/progress/report/share` | Generate shareable report link |

---

### 3.5 Multi-Language Service

**AWS Services:** Amazon Translate, Amazon Bedrock, Amazon ElastiCache (Redis), Amazon S3, AWS Lambda

**Purpose:** Provides content translation and localization, preserving technical accuracy.

**Translation Pipeline:**

```
Content Request (in preferred language)
       │
       ▼
┌──────────────────┐     HIT
│  ElastiCache     │──────────→ Return cached translation
│  (Redis)         │
│  TTL: 7 days     │
└───────┬──────────┘
        │ MISS
        ▼
┌──────────────────┐
│  Pre-translated  │     HIT
│  Content (S3)    │──────────→ Return & cache
│  Static library  │
└───────┬──────────┘
        │ MISS
        ▼
┌──────────────────┐
│  Translation     │
│  Pipeline        │
│  ├─ Amazon       │
│  │  Translate    │──→ Base translation
│  │  (bulk text)  │
│  └─ Amazon       │
│     Bedrock      │──→ Technical term preservation
│     (refinement) │    + contextual explanation
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│  Quality Check   │
│  ├─ Glossary     │──→ Verify technical terms unchanged
│  │  validation   │
│  └─ Code block   │──→ Ensure code snippets preserved
│     preservation │
└───────┬──────────┘
        │
        ▼
  Cache in Redis + Return
```

**Technical Glossary Management:**
```typescript
// Stored in S3 as JSON, loaded into Lambda at cold start
interface TechnicalGlossary {
  language: SupportedLanguage;
  terms: {
    english: string;              // "Binary Search Tree"
    transliterated: string;       // "बाइनरी सर्च ट्री" (Hindi)
    explanation: string;          // Vernacular explanation
    preserveEnglish: boolean;     // true for code terms like "API", "HTTP"
    category: string;             // "data_structures", "algorithms", etc.
  }[];
  lastUpdated: Date;
  version: number;
}
```

**Supported Languages (Phase 1):**
| Language | Code | Amazon Translate Support | Bedrock Refinement |
|----------|------|------------------------|--------------------|
| English | `en` | Native | N/A |
| Hindi | `hi` | Yes | Yes |
| Tamil | `ta` | Yes | Yes |
| Telugu | `te` | Yes | Yes |
| Bengali | `bn` | Yes | Yes |
| Marathi | `mr` | Yes | Yes |

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/translate` | Translate content on-demand |
| GET | `/api/translate/glossary/:lang` | Get technical glossary |
| PUT | `/api/translate/preference` | Update language preference |

---

### 3.6 Interview Simulation Service

**AWS Services:** Amazon Bedrock (Claude 3.5 Sonnet), AWS Lambda, Amazon DynamoDB, Amazon S3

**Purpose:** Provides AI-powered mock interviews aligned with target role and company.

**Interview Flow:**

```
Student starts interview session
       │
       ▼
Lambda: interview-start
  ├─ Load student profile & target role
  ├─ Select question set (DynamoDB question bank)
  ├─ Configure difficulty based on performance history
  └─ Initialize session in DynamoDB
       │
       ▼
For each question:
  ┌─────────────────────────────┐
  │ Bedrock: Generate question  │
  │ (role-specific, adaptive)   │
  ├─────────────────────────────┤
  │ Student submits answer      │
  ├─────────────────────────────┤
  │ Bedrock: Evaluate answer    │
  │ ├─ Correctness score        │
  │ ├─ Approach analysis        │
  │ ├─ Time complexity check    │
  │ ├─ Communication feedback   │
  │ └─ Improvement suggestions  │
  └─────────────────────────────┘
       │
       ▼
Lambda: interview-complete
  ├─ Aggregate scores
  ├─ Generate overall feedback (Bedrock)
  ├─ Update performance history (DynamoDB)
  └─ Adjust future difficulty
```

**Company-Specific Formats:**
| Company | Focus Areas | Special Format |
|---------|------------|----------------|
| Amazon | Leadership Principles, DSA, System Design | STAR method behavioral, LP-aligned |
| Google | DSA (hard), System Design, Googliness | Open-ended design, coding efficiency |
| Microsoft | DSA, Design, Problem Solving | Collaborative problem solving |
| Flipkart | DSA, HLD, LLD | E-commerce domain scenarios |
| Infosys | Aptitude, Programming, Communication | Mixed MCQ + coding |

**Data Model:**
```typescript
// DynamoDB — PK: studentId, SK: sessionId
interface InterviewSession {
  sessionId: string;
  studentId: string;
  type: 'coding' | 'system_design' | 'behavioral' | 'technical' | 'mixed';
  targetRole: TargetRole;
  targetCompany?: string;
  difficulty: 'easy' | 'medium' | 'hard';
  language: SupportedLanguage;
  durationMinutes: number;         // 30, 45, or 60
  questions: InterviewQuestion[];
  startedAt: Date;
  completedAt?: Date;
  performance: {
    overallScore: number;          // 0-100
    strengths: string[];
    weaknesses: string[];
    detailedFeedback: string;
    companyReadiness: number;      // 0-100 for target company
    recommendedNextDifficulty: 'easy' | 'medium' | 'hard';
  };
  bedrockMetadata: {
    modelId: string;
    totalTokens: number;
    latencyMs: number;
  };
}

interface InterviewQuestion {
  questionId: string;
  type: 'coding' | 'system_design' | 'behavioral' | 'technical_theory';
  difficulty: 'easy' | 'medium' | 'hard';
  topic: string;
  question: string;
  hints: string[];
  expectedApproach: string;
  optimalSolution?: string;
  studentAnswer: string;
  timeSpentSeconds: number;
  evaluation: {
    score: number;                 // 0-100
    correctness: number;
    approach: number;
    efficiency: number;
    communication: number;
    feedback: string;
    improvementTips: string[];
  };
}
```

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/interview/start` | Start new interview session |
| GET | `/api/interview/:sessionId` | Get session details |
| POST | `/api/interview/:sessionId/answer` | Submit answer for current question |
| POST | `/api/interview/:sessionId/hint` | Request hint |
| POST | `/api/interview/:sessionId/complete` | End session early / complete |
| GET | `/api/interview/history` | List past sessions |
| GET | `/api/interview/analytics` | Interview performance trends |

---

### 3.7 Content & Resource Management Service

**AWS Services:** Amazon OpenSearch Serverless, Amazon S3, AWS Lambda, Amazon DynamoDB

**Purpose:** Manages curated learning resources with intelligent search and recommendation.

**Data Model:**
```typescript
// Amazon OpenSearch index + S3 metadata
interface Resource {
  resourceId: string;
  title: string;
  type: 'video' | 'article' | 'problem' | 'documentation' | 'project' | 'course';
  url: string;
  provider: string;               // "leetcode", "youtube", "gfg", etc.
  skills: string[];
  topics: string[];
  difficulty: 'beginner' | 'intermediate' | 'advanced';
  estimatedMinutes: number;
  languages: SupportedLanguage[];
  qualityScore: number;           // 0-100, computed from ratings + curation
  isPaid: boolean;
  price?: { amount: number; currency: string };
  rating: number;
  reviewCount: number;
  bookmarkCount: number;
  tags: string[];
  lastVerified: Date;             // link still works
  lastUpdated: Date;
  isActive: boolean;
}

// DynamoDB — PK: studentId, SK: resourceId
interface Bookmark {
  studentId: string;
  resourceId: string;
  savedAt: Date;
  notes?: string;
  rating?: number;
  completed: boolean;
}
```

**API Endpoints:**
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/resources/recommended` | AI-recommended resources for current phase |
| GET | `/api/resources/search?q=&type=&difficulty=&lang=` | Full-text search |
| POST | `/api/resources/bookmark` | Bookmark a resource |
| DELETE | `/api/resources/bookmark/:resourceId` | Remove bookmark |
| GET | `/api/resources/bookmarks` | List bookmarked resources |
| POST | `/api/resources/:resourceId/rate` | Rate a resource |

---

### 3.8 Adaptive Learning Engine

**AWS Services:** Amazon SageMaker (custom model), AWS Lambda, Amazon EventBridge, Amazon SNS

**Purpose:** Continuously adjusts learning path difficulty and pacing based on student performance.

**Adaptation Rules:**

```
┌─────────────────────────────────────────────────────────────────┐
│                    ADAPTIVE LEARNING RULES                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  Rule 1: STRUGGLING DETECTION                                   │
│  IF completion_rate < 50% for 3 consecutive days                │
│  THEN reduce daily_task_load by 20%                             │
│       add easier prerequisite modules                            │
│       increase explanation depth in daily tasks                  │
│       notify student with encouragement                          │
│                                                                  │
│  Rule 2: ACCELERATION                                           │
│  IF completion_rate > 90% for 5 consecutive days                │
│  AND avg_problem_accuracy > 80%                                 │
│  THEN offer accelerated path option                             │
│       increase problem difficulty                                │
│       add advanced topics                                        │
│       notify student of opportunity                              │
│                                                                  │
│  Rule 3: STALL DETECTION                                        │
│  IF same topic attempted > 5 times without passing              │
│  THEN suggest alternative learning format                        │
│       (video ↔ text ↔ project-based)                            │
│       provide targeted micro-explanations (Bedrock)              │
│                                                                  │
│  Rule 4: TIME REBALANCING                                       │
│  IF actual_time consistently > estimated_time by > 30%          │
│  THEN recalibrate time estimates                                 │
│       reduce daily task count to match real pace                 │
│                                                                  │
│  Rule 5: STRENGTH REINFORCEMENT                                 │
│  IF skill_score > 85% on assessment                             │
│  THEN reduce review frequency for that skill                    │
│       reallocate time to weaker areas                            │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 4. Database Design

### 4.1 Amazon RDS Aurora PostgreSQL (Relational Data)

```sql
-- Students table (core profile)
CREATE TABLE students (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    cognito_sub VARCHAR(128) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    college VARCHAR(255),
    college_tier SMALLINT CHECK (college_tier IN (1, 2, 3)),
    state VARCHAR(100),
    graduation_year INTEGER,
    degree VARCHAR(100),
    major VARCHAR(100),
    is_cs_background BOOLEAN DEFAULT false,
    current_year SMALLINT,
    cgpa DECIMAL(3,2),
    target_role VARCHAR(50) NOT NULL,
    target_companies JSONB DEFAULT '[]',
    dream_company VARCHAR(100),
    desired_start_date DATE,
    hours_per_day SMALLINT DEFAULT 2,
    days_per_week SMALLINT DEFAULT 5,
    preferred_time_slots JSONB DEFAULT '[]',
    timezone VARCHAR(50) DEFAULT 'Asia/Kolkata',
    primary_language VARCHAR(5) DEFAULT 'en',
    secondary_languages JSONB DEFAULT '[]',
    learning_style VARCHAR(20) DEFAULT 'mixed',
    notification_prefs JSONB DEFAULT '{"email":true,"push":true,"sms":false}',
    onboarding_completed BOOLEAN DEFAULT false,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_students_cognito ON students(cognito_sub);
CREATE INDEX idx_students_email ON students(email);
CREATE INDEX idx_students_role ON students(target_role);
CREATE INDEX idx_students_timezone ON students(timezone);

-- Student skills
CREATE TABLE student_skills (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    skill_name VARCHAR(100) NOT NULL,
    category VARCHAR(50) NOT NULL,
    level VARCHAR(20) NOT NULL,
    score SMALLINT CHECK (score BETWEEN 0 AND 100),
    assessed_via VARCHAR(30) DEFAULT 'self',
    confidence_score DECIMAL(3,2) DEFAULT 0.50,
    last_assessed TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, skill_name)
);

CREATE INDEX idx_skills_student ON student_skills(student_id);

-- Progress records (partitioned by month)
CREATE TABLE progress_records (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES students(id),
    date DATE NOT NULL,
    tasks_completed SMALLINT DEFAULT 0,
    tasks_total SMALLINT DEFAULT 0,
    tasks_skipped SMALLINT DEFAULT 0,
    minutes_spent INTEGER DEFAULT 0,
    minutes_estimated INTEGER DEFAULT 0,
    problems_solved SMALLINT DEFAULT 0,
    problems_attempted SMALLINT DEFAULT 0,
    avg_problem_accuracy DECIMAL(5,2) DEFAULT 0,
    quiz_score DECIMAL(5,2) DEFAULT 0,
    interviews_practiced SMALLINT DEFAULT 0,
    interview_avg_score DECIMAL(5,2) DEFAULT 0,
    login_streak INTEGER DEFAULT 0,
    session_count SMALLINT DEFAULT 0,
    readiness_score DECIMAL(5,2) DEFAULT 0,
    completion_rate DECIMAL(5,2) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(student_id, date)
) PARTITION BY RANGE (date);

-- Create monthly partitions (example)
CREATE TABLE progress_records_2026_01 PARTITION OF progress_records
    FOR VALUES FROM ('2026-01-01') TO ('2026-02-01');
CREATE TABLE progress_records_2026_02 PARTITION OF progress_records
    FOR VALUES FROM ('2026-02-01') TO ('2026-03-01');

CREATE INDEX idx_progress_student_date ON progress_records(student_id, date DESC);

-- Resources
CREATE TABLE resources (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500) NOT NULL,
    type VARCHAR(30) NOT NULL,
    url TEXT NOT NULL,
    provider VARCHAR(100),
    skills JSONB DEFAULT '[]',
    topics JSONB DEFAULT '[]',
    difficulty VARCHAR(20) DEFAULT 'intermediate',
    estimated_minutes INTEGER,
    languages JSONB DEFAULT '["en"]',
    quality_score SMALLINT DEFAULT 50,
    is_paid BOOLEAN DEFAULT false,
    price_amount DECIMAL(10,2),
    price_currency VARCHAR(3) DEFAULT 'INR',
    rating DECIMAL(3,2) DEFAULT 0,
    review_count INTEGER DEFAULT 0,
    bookmark_count INTEGER DEFAULT 0,
    tags JSONB DEFAULT '[]',
    is_active BOOLEAN DEFAULT true,
    last_verified TIMESTAMPTZ,
    last_updated TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_resources_type ON resources(type);
CREATE INDEX idx_resources_difficulty ON resources(difficulty);
CREATE INDEX idx_resources_skills ON resources USING GIN(skills);
CREATE INDEX idx_resources_quality ON resources(quality_score DESC);
```

### 4.2 Amazon DynamoDB (NoSQL — High-Velocity Data)

| Table | Partition Key | Sort Key | Purpose | GSI |
|-------|-------------|----------|---------|-----|
| `roadmaps` | `studentId` | `roadmapId` | Roadmap documents | GSI1: `status`-`createdAt` |
| `daily-plans` | `studentId` | `date` | Daily task plans | GSI1: `status`-`date` |
| `tasks` | `planId` | `taskId` | Individual tasks | GSI1: `studentId`-`status` |
| `interview-sessions` | `studentId` | `sessionId` | Mock interview data | GSI1: `type`-`createdAt` |
| `interview-questions` | `questionId` | `—` | Question bank | GSI1: `type`-`difficulty`, GSI2: `topic`-`role` |
| `spaced-repetition` | `studentId` | `skillId` | SR scheduling state | GSI1: `nextReviewDate` |
| `gamification` | `studentId` | `—` | Badges, XP, streaks | GSI1: `xp` (leaderboard) |
| `bookmarks` | `studentId` | `resourceId` | Saved resources | — |
| `jd-cache` | `companyRole` | `scrapedAt` | Cached JD analysis | GSI1: `role`-`company` |

**DynamoDB Capacity Planning:**
- Mode: **On-Demand** (Phase 1) — auto-scales, no capacity planning needed
- Transition to **Provisioned + Auto Scaling** when traffic patterns stabilize
- Enable **Point-in-Time Recovery (PITR)** on all tables
- Enable **DynamoDB Streams** on `tasks` table for real-time progress aggregation

---

## 5. AI/ML Architecture

### 5.1 Amazon Bedrock — Generative AI

| Use Case | Model | Max Tokens | Temperature | Estimated Cost/Request |
|----------|-------|------------|-------------|-----------------------|
| Roadmap generation | Claude 3.5 Sonnet | 4096 | 0.3 | ~$0.05 |
| Interview question gen | Claude 3.5 Sonnet | 2048 | 0.5 | ~$0.02 |
| Answer evaluation | Claude 3.5 Sonnet | 2048 | 0.2 | ~$0.02 |
| Content explanation | Claude 3.5 Haiku | 1024 | 0.4 | ~$0.005 |
| JD analysis | Claude 3.5 Haiku | 1024 | 0.1 | ~$0.005 |
| Translation refinement | Claude 3.5 Haiku | 512 | 0.1 | ~$0.003 |

**Bedrock Guardrails:**
- Content filtering: Block harmful/irrelevant content
- PII redaction: Remove sensitive data from prompts
- Token budget: Hard limit per request to control costs
- Fallback: If Bedrock unavailable, serve cached/template responses

### 5.2 Amazon SageMaker — Custom ML Models

| Model | Type | Training Data | Endpoint |
|-------|------|---------------|----------|
| Skill Assessment | Classification + Regression | Assessment responses, coding performance | Serverless Inference |
| Adaptive Difficulty | Reinforcement Learning | Task completion patterns, engagement metrics | Serverless Inference |
| Resource Recommender | Collaborative Filtering | User-resource interactions, ratings | Serverless Inference |
| Retention Predictor | Time-Series | Login streaks, engagement decay patterns | Serverless Inference |

**SageMaker Configuration:**
- **Endpoint type:** Serverless Inference (cost-effective, scales to zero)
- **Model storage:** Amazon S3
- **Training:** SageMaker Training Jobs (scheduled monthly retraining)
- **Monitoring:** SageMaker Model Monitor for data/model drift

### 5.3 Amazon Translate + Comprehend

**Translation Pipeline:**
1. **Amazon Comprehend:** Detect language, extract entities (preserve technical terms)
2. **Amazon Translate:** Base translation (Custom Terminology for tech terms)
3. **Amazon Bedrock (Haiku):** Refine translation for natural technical explanation
4. **Quality validation:** Check against glossary, preserve code blocks

**Custom Terminology (Amazon Translate):**
- Upload CSV mapping: English term → Target language term
- Example: `API` → `API` (preserve), `Binary Tree` → `बाइनरी ट्री` (transliterate)
- Maintained per language, version controlled in S3

---

## 6. Security Architecture

### 6.1 Authentication & Authorization (Amazon Cognito)

```
┌──────────────────────────────────────────────────┐
│                Amazon Cognito                     │
│                                                   │
│  User Pool: campus-hire-users                     │
│  ├── Sign-up: Email + Password (min 8 chars)     │
│  ├── MFA: Optional TOTP / SMS                    │
│  ├── Email verification: Required                 │
│  ├── Password policy: 1 upper, 1 lower, 1 digit │
│  ├── Account recovery: Email                      │
│  └── Custom attributes: college, role, language   │
│                                                   │
│  App Client: campus-hire-web                      │
│  ├── OAuth 2.0: Authorization Code + PKCE        │
│  ├── Token validity: Access=1hr, Refresh=30days  │
│  └── Scopes: openid, email, profile              │
│                                                   │
│  Groups (RBAC):                                   │
│  ├── student: Default role                        │
│  ├── admin: Platform administration               │
│  └── content-manager: Resource curation           │
└──────────────────────────────────────────────────┘
```

### 6.2 API Security

| Layer | Mechanism | AWS Service |
|-------|-----------|-------------|
| Edge Protection | DDoS mitigation, bot detection | AWS WAF + Shield |
| API Authentication | JWT validation | Cognito Authorizer on API Gateway |
| Rate Limiting | Per-user throttling | API Gateway Usage Plans |
| Input Validation | Schema validation | API Gateway Request Validators |
| Encryption (transit) | TLS 1.3 | CloudFront + ALB |
| Encryption (rest) | AES-256 | AWS KMS |
| Secret Management | API keys, DB credentials | AWS Secrets Manager |
| Audit Logging | API access logs | CloudTrail + CloudWatch |

### 6.3 Data Protection & Compliance

- **Data residency:** All data stored in `ap-south-1` (Mumbai)
- **DPDP Act 2023:** Consent management, data portability, right to deletion
- **GDPR:** Cookie consent, data export API, account deletion workflow
- **PII handling:** Encrypted fields for email, phone, name; anonymized for analytics
- **Backup encryption:** RDS snapshots and S3 backups encrypted with KMS CMK
- **Access logging:** CloudTrail enabled for all API calls; S3 access logging for content buckets

---

## 7. Infrastructure & Deployment

### 7.1 Infrastructure as Code (AWS CDK)

```
infrastructure/
├── bin/
│   └── campus-hire.ts              # CDK app entry
├── lib/
│   ├── stacks/
│   │   ├── network-stack.ts        # VPC, subnets, security groups
│   │   ├── database-stack.ts       # RDS Aurora, DynamoDB, ElastiCache
│   │   ├── compute-stack.ts        # Lambda functions, ECS Fargate
│   │   ├── api-stack.ts            # API Gateway, Cognito
│   │   ├── ai-stack.ts             # Bedrock, SageMaker endpoints
│   │   ├── storage-stack.ts        # S3 buckets, CloudFront
│   │   ├── messaging-stack.ts      # SQS, SNS, SES, EventBridge
│   │   ├── search-stack.ts         # OpenSearch Serverless
│   │   ├── monitoring-stack.ts     # CloudWatch, X-Ray, alarms
│   │   └── cicd-stack.ts           # CodePipeline, CodeBuild
│   └── constructs/
│       ├── lambda-api.ts           # Reusable Lambda + API GW construct
│       └── dynamo-table.ts         # Reusable DynamoDB table construct
├── cdk.json
└── tsconfig.json
```

### 7.2 CI/CD Pipeline (AWS CodePipeline)

```
┌─────────────┐    ┌─────────────┐    ┌──────────────┐    ┌──────────────┐
│   Source     │    │    Build    │    │   Staging    │    │  Production  │
│   (GitHub)   │───→│  (CodeBuild)│───→│  (Deploy +   │───→│  (Blue/Green │
│              │    │  ├─ Lint    │    │   E2E Test)  │    │   Deploy)    │
│  Push to     │    │  ├─ Test   │    │              │    │              │
│  main branch │    │  ├─ Build  │    │  Auto-approve│    │  Manual gate │
│              │    │  └─ CDK    │    │  if tests    │    │  (approval)  │
│              │    │    synth   │    │  pass        │    │              │
└─────────────┘    └─────────────┘    └──────────────┘    └──────────────┘
```

**Pipeline Stages:**
1. **Source:** GitHub webhook triggers pipeline on `main` push
2. **Build:** CodeBuild runs lint, unit tests, integration tests, builds artifacts, `cdk synth`
3. **Staging:** Deploy to staging environment, run E2E tests, auto-approve if green
4. **Production:** Blue/green deployment via CodeDeploy, manual approval gate, automated rollback on alarm

### 7.3 Environment Configuration

| Environment | AWS Account | Region | Scale | Purpose |
|-------------|------------|--------|-------|---------|
| Development | Dev Account | ap-south-1 | Minimal | Developer testing |
| Staging | Staging Account | ap-south-1 | 1/4 of prod | Pre-production validation |
| Production | Prod Account | ap-south-1 | Full | Live users |
| DR | Prod Account | ap-southeast-1 | Hot standby | Disaster recovery |

---

## 8. Technology Stack — Final

### Frontend
| Technology | Purpose |
|-----------|---------|
| Next.js 14+ (App Router) | React framework with SSR/SSG |
| TypeScript | Type safety |
| Tailwind CSS | Utility-first styling |
| Zustand | Lightweight state management |
| TanStack Query | Server state + caching |
| Recharts | Data visualization (progress charts) |
| next-intl | i18n/l10n for multi-language UI |
| next-pwa | Progressive Web App support |

### Backend
| Technology | Purpose |
|-----------|---------|
| Node.js 20.x (Lambda) | Serverless API handlers |
| TypeScript | Type safety |
| Middy | Lambda middleware framework |
| Zod | Runtime input validation |
| Prisma | ORM for Aurora PostgreSQL |
| AWS SDK v3 | AWS service integration |

### AI/ML
| Technology | Purpose |
|-----------|---------|
| Amazon Bedrock (Claude 3.5) | Generative AI tasks |
| Amazon SageMaker | Custom ML model hosting |
| Amazon Translate | Multi-language translation |
| Amazon Comprehend | NLP entity extraction |
| LangChain.js | LLM orchestration & prompt management |

### Infrastructure
| Technology | Purpose |
|-----------|---------|
| AWS CDK (TypeScript) | Infrastructure as Code |
| Docker | Container images for ECS Fargate |
| AWS CodePipeline | CI/CD orchestration |
| AWS CodeBuild | Build & test execution |
| GitHub | Source control |

### Monitoring
| Technology | Purpose |
|-----------|---------|
| Amazon CloudWatch | Logs, metrics, alarms |
| AWS X-Ray | Distributed tracing |
| Amazon QuickSight | Admin BI dashboards |
| AWS CloudTrail | Audit logging |

---

## 9. Performance Optimization

### 9.1 Caching Strategy

| Data | Cache Location | TTL | Invalidation |
|------|---------------|-----|--------------|
| Student session | ElastiCache Redis | 1 hour | On logout |
| Daily plan | ElastiCache Redis | 24 hours | On plan regeneration |
| Active roadmap | ElastiCache Redis | 7 days | On roadmap update |
| Translated content | ElastiCache Redis | 7 days | On glossary update |
| Static assets | CloudFront | 30 days | Versioned URLs |
| Resource search | OpenSearch | Realtime | On resource CRUD |
| Technical glossary | Lambda memory | Until cold start | Redeploy |

### 9.2 Lambda Optimization

- **Provisioned Concurrency:** 10 instances for `daily-plan-generate` and `profile-get` (critical path)
- **ARM64 (Graviton2):** All Lambda functions run on ARM for 20% cost savings + better performance
- **Bundling:** esbuild for tree-shaking, < 5MB deployment packages
- **Layers:** Shared AWS SDK, Prisma client, and utilities in Lambda Layers
- **Connection pooling:** RDS Proxy for Aurora PostgreSQL connections from Lambda

### 9.3 Database Optimization

- **Aurora:** Read replicas for analytics queries; connection pooling via RDS Proxy
- **DynamoDB:** On-demand capacity; DAX (DynamoDB Accelerator) if hot-key issues arise
- **Partitioning:** Progress records partitioned by month in Aurora
- **Indexing:** GSIs on DynamoDB for access patterns; B-tree indexes on RDS for frequent queries

---

## 10. Monitoring & Observability

### 10.1 CloudWatch Dashboards

**System Health Dashboard:**
- Lambda invocation count, errors, duration (p50, p95, p99)
- API Gateway 4xx/5xx error rates
- RDS Aurora CPU, connections, query latency
- DynamoDB consumed read/write capacity
- ElastiCache hit rate, memory usage

**Business Metrics Dashboard:**
- Daily active users
- Task completion rate (daily)
- Roadmap generation count
- Interview sessions per day
- Average readiness score trend

### 10.2 Alerting

| Alarm | Threshold | Action |
|-------|-----------|--------|
| API error rate | > 5% for 5 min | SNS → PagerDuty/Slack |
| Lambda duration | p95 > 10s for 10 min | SNS → Slack |
| RDS CPU | > 80% for 15 min | Auto-scale read replica |
| DynamoDB throttled | > 0 for 5 min | SNS → Slack |
| Bedrock latency | p95 > 30s for 5 min | SNS → Slack, fallback to cache |
| Daily plan generation failures | > 1% of batch | SNS → PagerDuty |
| CloudFront error rate | > 1% for 10 min | SNS → Slack |

### 10.3 Distributed Tracing (X-Ray)

Trace path for critical flows:
```
CloudFront → API Gateway → Lambda → [RDS | DynamoDB | Bedrock | Translate]
```
- All Lambda functions instrumented with X-Ray SDK
- Custom subsegments for Bedrock calls (track model latency separately)
- Sampling: 5% of requests in production, 100% in staging

---

## 11. Cost Estimation (10K MAU)

### Monthly AWS Cost Breakdown

| Service | Configuration | Est. Monthly Cost |
|---------|--------------|-------------------|
| AWS Lambda | 5M invocations, 256-512MB, ARM64 | $150 |
| Amazon API Gateway | 5M requests | $20 |
| Amazon RDS Aurora Serverless v2 | 2-8 ACU, Multi-AZ | $400 |
| Amazon DynamoDB | On-Demand, ~50GB | $100 |
| Amazon ElastiCache (Redis) | cache.t4g.medium, 2 nodes | $120 |
| Amazon Bedrock | ~500K requests/month (mixed models) | $800 |
| Amazon SageMaker Serverless | 4 endpoints, sporadic traffic | $200 |
| Amazon S3 | 100GB storage + requests | $30 |
| Amazon CloudFront | 500GB transfer | $50 |
| Amazon OpenSearch Serverless | 2 OCU | $350 |
| Amazon Cognito | 10K MAU | $50 |
| Amazon Translate | ~10M characters/month | $150 |
| Amazon SES/SNS | 500K emails, 200K notifications | $80 |
| Amazon EventBridge/SQS/Step Functions | Messaging & orchestration | $30 |
| CloudWatch / X-Ray | Logging, metrics, tracing | $100 |
| Data Transfer | Inter-service + internet | $100 |
| **TOTAL** | | **~$2,730/month** |

**Cost per MAU:** ~$0.27 (well within $0.50 target)

**Cost Optimization Strategies:**
- Lambda ARM64 (Graviton2): 20% savings
- SageMaker Serverless Inference: Scale to zero
- DynamoDB On-Demand: No over-provisioning
- Aurora Serverless v2: Auto-scales to minimum
- CloudFront caching: Reduce origin requests
- Reserved Instances (Phase 2): 30-40% savings on steady-state compute
- Savings Plans for Lambda compute

---

## 12. Correctness Properties

### 12.1 Roadmap Generation

| Property | Invariant | Validates |
|----------|-----------|-----------|
| Prerequisite Ordering | If skill B requires skill A, module(A).order < module(B).order in every roadmap | Req 3.2.7 |
| Time Constraint | total_estimated_hours ≤ (hours_per_day × days_per_week / 7 × duration_days) | Req 3.2.5 |
| Skill Gap Coverage | ∀ gap ∈ identified_gaps: ∃ module ∈ roadmap where module.skills ∩ gap ≠ ∅ | Req 3.2.4 |
| Alternative Paths | |roadmap.alternativePaths| ≥ 2 | Req 3.2.6 |

### 12.2 Daily Plans

| Property | Invariant | Validates |
|----------|-----------|-----------|
| Time Budget | Σ task.estimatedMinutes ≤ student.availableMinutes(today) | Req 3.3.2 |
| Task Diversity | |{task.type : task ∈ plan}| ≥ 2 | Req 3.3.3 |
| Progress Continuity | ∀ task ∈ plan: task.milestoneId = current_milestone OR task.isSpacedRepetition | Req 3.3.1 |
| Carry-Forward | yesterday.incomplete_tasks ⊆ today.tasks (with boosted priority) | Req 3.3.8 |

### 12.3 Progress Tracking

| Property | Invariant | Validates |
|----------|-----------|-----------|
| Completion Consistency | milestone.status = 'completed' → ∀ module ∈ milestone: module.status = 'completed' | Req 3.6.1 |
| Score Monotonicity | task_completed → readiness_score(t+1) ≥ readiness_score(t) (unless new assessment) | Req 3.6.3 |
| Analytics Accuracy | Σ daily_minutes_spent = total_minutes_spent across all tasks | Req 3.6.4 |

### 12.4 Translation

| Property | Invariant | Validates |
|----------|-----------|-----------|
| Code Preservation | translated_content.code_blocks = original_content.code_blocks (byte-identical) | Req 3.5.5 |
| Language Consistency | ∀ response in session: response.language = session.selectedLanguage | Req 3.5.1 |
| Term Preservation | ∀ term ∈ glossary.preserveEnglish: term appears unchanged in translation | Req 3.5.5 |

### 12.5 Adaptive Learning

| Property | Invariant | Validates |
|----------|-----------|-----------|
| Struggle Response | completion_rate < 50% for 3 days → next_day.task_load ≤ current × 0.8 | Req 3.10.2 |
| Acceleration | completion_rate > 90% for 5 days → difficulty_increased OR pace_increased | Req 3.10.4 |
| Interview Difficulty | success_rate > 80% → next_session.difficulty > current | Req 3.7.4 |

---

## 13. Testing Strategy

### 13.1 Unit Tests
- **Framework:** Jest + ts-jest
- **Coverage target:** 80%+
- **Scope:** Lambda handlers, business logic, utility functions
- **Mocks:** AWS SDK mocked via `aws-sdk-client-mock`

### 13.2 Integration Tests
- **Framework:** Jest + Supertest
- **Scope:** API endpoints end-to-end against local DynamoDB + PostgreSQL (Docker)
- **Includes:** Cognito token validation (mocked), database interactions, SQS message handling

### 13.3 Property-Based Tests
- **Framework:** fast-check (TypeScript)
- **Scope:** All correctness properties from Section 12
- **Run on:** Every CI/CD build

### 13.4 E2E Tests
- **Framework:** Playwright
- **Scope:** Critical user flows (onboarding, roadmap generation, daily plan, interview)
- **Environment:** Staging (full AWS stack)
- **Browsers:** Chrome, Firefox, Safari, Mobile Chrome

### 13.5 Load Tests
- **Tool:** Artillery
- **Scenarios:** 10K concurrent users, daily plan generation burst, Bedrock throughput
- **Run on:** Pre-release to staging

### 13.6 Security Tests
- **Tools:** OWASP ZAP, AWS Inspector
- **Scope:** OWASP Top 10, Cognito configuration, IAM least-privilege, S3 bucket policies
- **Frequency:** Monthly automated + quarterly manual pen-test

---

## 14. Disaster Recovery

### 14.1 DR Strategy

| Component | DR Mechanism | RTO | RPO |
|-----------|-------------|-----|-----|
| RDS Aurora | Cross-region read replica (ap-southeast-1) | 30 min | ~5 min |
| DynamoDB | Global Tables (ap-southeast-1) | < 1 min | < 1 sec |
| S3 | Cross-region replication | < 1 min | < 15 min |
| Lambda | Multi-region deployment via CDK | 15 min | 0 (stateless) |
| CloudFront | Origin failover to DR region | Automatic | 0 |
| Cognito | User pool data export + re-import | 1 hour | Daily backup |

### 14.2 Failover Procedure

1. CloudWatch alarm detects primary region failure
2. Route 53 health check fails → automatic DNS failover to DR
3. CloudFront failover origin activates (DR region ALB/API Gateway)
4. Aurora promotes read replica to primary in DR region
5. DynamoDB Global Tables serve from DR region automatically
6. SNS alert to ops team for manual verification

---

## 15. Future Enhancements

### Phase 2 (Month 4–8)
- React Native mobile apps (iOS, Android)
- Peer-to-peer study groups and mentoring
- Live coding collaboration sessions
- Company-specific deep-dive preparation tracks
- Resume builder with AI review
- Voice-based interview simulation (Amazon Polly + Transcribe)

### Phase 3 (Month 9–12)
- Employer dashboard for campus recruitment
- Direct job application integration
- Career counseling AI chatbot (Bedrock Agents)
- Community forums and discussion boards
- Salary benchmarking and negotiation guidance
- Certification preparation tracks (AWS, Google Cloud, etc.)

---

## 16. Success Criteria

The platform will be considered successful when:

1. **70%+** daily active user rate among registered students
2. **60%+** task completion rate across all users
3. **+30 point** average readiness score improvement within 60 days
4. **NPS > 50** (80%+ user satisfaction)
5. **40%+** interview conversion rate for roadmap completers
6. **< 2 second** average page load time
7. **99.9%** uptime
8. **6 languages** supported with 90%+ translation accuracy
9. **< $0.30** cost per monthly active user
10. **< 90 days** average time to job-ready status
