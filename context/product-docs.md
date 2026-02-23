# TechCorp Platform - Product Documentation

> **Version:** 3.2.1 | **Last Updated:** 2025-12-15 | **Status:** Current

This document serves as the comprehensive knowledge base for TechCorp Platform. It covers all features, workflows, troubleshooting procedures, and integration guides needed to support customers.

---

## Table of Contents

1. [Getting Started](#1-getting-started)
2. [Account Management](#2-account-management)
3. [Core Features](#3-core-features)
4. [Integrations](#4-integrations)
5. [Troubleshooting](#5-troubleshooting)
6. [Common Error Codes](#6-common-error-codes)
7. [FAQ](#7-frequently-asked-questions)

---

## 1. Getting Started

### 1.1 System Requirements

| Component         | Requirement                                |
|-------------------|--------------------------------------------|
| Browser           | Chrome 90+, Firefox 88+, Safari 15+, Edge 90+ |
| Internet          | Minimum 5 Mbps broadband                  |
| Screen Resolution | 1280x720 minimum (1920x1080 recommended)  |
| Mobile            | iOS 14.0+ / Android 10.0+                 |
| Desktop App       | Windows 10+, macOS 11+, Ubuntu 20.04+     |

### 1.2 Account Creation

To create a new TechCorp account:

1. Navigate to **https://app.techcorp.io/signup**
2. Enter your **work email address** (personal emails like Gmail/Yahoo are accepted for trials)
3. Choose a **strong password** (minimum 8 characters, must include uppercase, lowercase, number, and special character)
4. Enter your **full name** and **company name**
5. Click **"Create Account"**
6. Check your email inbox for a **verification email** (check spam/junk if not received within 5 minutes)
7. Click the **verification link** in the email (link expires after 24 hours)
8. You will be redirected to the **Onboarding Wizard**

**Note:** If the verification email does not arrive:
- Check spam/junk folders
- Ensure the email address was typed correctly
- Click "Resend Verification Email" on the signup page
- Contact support if issues persist after 15 minutes

### 1.3 Onboarding Wizard

After email verification, the Onboarding Wizard guides you through initial setup:

**Step 1 - Team Setup:**
- Name your workspace (e.g., "Marketing Team" or "Engineering")
- This becomes your team URL: `https://app.techcorp.io/your-team-name`
- Team names must be unique, 3-50 characters, alphanumeric and hyphens only

**Step 2 - Invite Members:**
- Enter email addresses of team members (comma-separated for bulk invites)
- Set initial roles: Admin, Manager, Member, or Viewer
- Members receive an invitation email with a join link
- Invitations expire after 7 days; can be resent from Team Settings

**Step 3 - Choose a Template:**
- **Blank Project** - Start from scratch
- **Software Development** - Sprints, backlog, bug tracking
- **Marketing Campaign** - Campaign planning, content calendar
- **Product Launch** - Launch checklist, milestones, tasks
- **Client Onboarding** - Client milestones and deliverables
- **Event Planning** - Timeline, vendor management, logistics

**Step 4 - Preferences:**
- Select your timezone
- Choose date format (MM/DD/YYYY or DD/MM/YYYY)
- Enable/disable email notifications
- Choose default task view (List, Kanban, or Calendar)

### 1.4 First Project Setup

After the Onboarding Wizard:

1. Click **"+ New Project"** in the sidebar
2. Enter a **project name** (required) and **description** (optional)
3. Select a **template** or choose "Blank"
4. Set **project visibility**: Private (only invited members) or Team-wide (all team members)
5. Set **project dates** (optional start and end dates)
6. Click **"Create Project"**

Your project dashboard will display:
- **Overview tab** - Project summary, progress metrics, recent activity
- **Tasks tab** - Task list/Kanban view
- **Timeline tab** - Gantt chart view
- **Files tab** - Shared documents and attachments
- **Settings tab** - Project-level configuration

---

## 2. Account Management

### 2.1 Password Reset

If you've forgotten your password:

1. Go to **https://app.techcorp.io/login**
2. Click **"Forgot Password?"** below the login form
3. Enter the **email address** associated with your account
4. Click **"Send Reset Link"**
5. Check your email for the password reset email (arrives within 2-5 minutes)
6. Click the **"Reset Password"** button in the email
7. Enter your **new password** (must meet the same complexity requirements: 8+ characters, uppercase, lowercase, number, special character)
8. Confirm the new password by typing it again
9. Click **"Update Password"**
10. You will be redirected to the login page. Log in with your new password.

**Important Notes:**
- Password reset links expire after **1 hour**
- You can only request **3 password resets per hour** (rate limited)
- If you do not receive the reset email, check spam/junk folders
- If your account has **two-factor authentication (2FA)** enabled, you will be prompted for your 2FA code after entering the new password
- Previous sessions on other devices will be **automatically logged out** after password change

### 2.2 Profile Updates

To update your profile information:

1. Click your **avatar** in the top-right corner
2. Select **"Profile Settings"**
3. Editable fields:
   - **Display Name** - Shown in comments, task assignments, and mentions
   - **Job Title** - Optional, shown in team directory
   - **Profile Photo** - Upload JPG/PNG, max 5 MB, recommended 200x200px
   - **Phone Number** - Optional, used for WhatsApp integration
   - **Timezone** - Affects all date/time displays
   - **Language** - English, Spanish, French, German, Portuguese, Japanese
   - **Notification Preferences** - Email, in-app, mobile push
4. Click **"Save Changes"**

### 2.3 Billing Management

Access billing from **Settings > Billing** (Admin role required).

**Viewing Current Plan:**
- Current plan name and price
- Billing cycle (monthly or annual)
- Next billing date
- Number of members used vs. included
- Storage used vs. included

**Updating Payment Method:**
1. Go to **Settings > Billing > Payment Methods**
2. Click **"Add Payment Method"**
3. Enter credit card details or connect via Stripe
4. Set as default payment method
5. Remove old payment methods if desired

**Viewing Invoice History:**
- Go to **Settings > Billing > Invoices**
- Download individual invoices as PDF
- Invoices include itemized charges, taxes, and payment method used

### 2.4 Subscription Changes

**Upgrading Your Plan:**
1. Go to **Settings > Billing > Plan**
2. Click **"Change Plan"**
3. Select the desired plan (Starter, Professional, Enterprise)
4. Review the pricing difference
5. Confirm the upgrade
6. Upgrade takes effect **immediately**; prorated charges apply

**Downgrading Your Plan:**
1. Go to **Settings > Billing > Plan**
2. Click **"Change Plan"**
3. Select a lower-tier plan
4. Review any features that will be lost
5. Confirm the downgrade
6. Downgrade takes effect at the **end of current billing cycle**
7. Data beyond the new plan's limits (e.g., storage) will be preserved but read-only

**Cancelling Your Subscription:**
1. Go to **Settings > Billing > Plan**
2. Click **"Cancel Subscription"**
3. Complete the cancellation survey (optional but appreciated)
4. Confirm cancellation
5. Access continues until end of current billing period
6. Data is retained for **30 days** after cancellation, then permanently deleted
7. You can reactivate within the 30-day window to restore all data

### 2.5 Two-Factor Authentication (2FA)

**Enabling 2FA:**
1. Go to **Profile Settings > Security**
2. Click **"Enable Two-Factor Authentication"**
3. Choose method:
   - **Authenticator App** (recommended) - Google Authenticator, Authy, 1Password
   - **SMS** - Text message to registered phone number
4. For Authenticator App:
   - Scan the QR code with your authenticator app
   - Enter the 6-digit code displayed in the app
   - Save your **recovery codes** (10 one-time-use codes) in a secure location
5. Click **"Verify and Enable"**

**Disabling 2FA:**
1. Go to **Profile Settings > Security**
2. Click **"Disable Two-Factor Authentication"**
3. Enter your current password and a valid 2FA code
4. Confirm the action

**Lost 2FA Access:**
- Use one of your **recovery codes** to log in
- If no recovery codes available, contact support with account verification (registered email + last 4 digits of payment method)
- Account recovery takes up to 24 hours for security verification

### 2.6 Team Management

**Inviting New Members:**
1. Go to **Settings > Team Members**
2. Click **"Invite Members"**
3. Enter email addresses (one per line or comma-separated)
4. Select role: Admin, Manager, Member, or Viewer
5. Optionally add to specific projects
6. Click **"Send Invitations"**

**Removing Members:**
1. Go to **Settings > Team Members**
2. Find the member in the list
3. Click the **three-dot menu** (...)
4. Select **"Remove from Team"**
5. Choose whether to reassign their tasks or leave them unassigned
6. Confirm the removal

**Changing Member Roles:**
1. Go to **Settings > Team Members**
2. Click on the member's current role
3. Select the new role from the dropdown
4. Click **"Save"**

---

## 3. Core Features

### 3.1 Projects

**Creating a Project:**
1. Click **"+ New Project"** in the left sidebar
2. Fill in project details:
   - **Name** (required): 1-100 characters
   - **Description** (optional): Rich text, up to 5,000 characters
   - **Color**: Choose a project color for visual identification
   - **Template**: Select from pre-built templates or blank
   - **Visibility**: Private or Team-wide
   - **Start/End Dates**: Optional project timeline
3. Click **"Create Project"**

**Project Templates:**
| Template              | Includes                                    | Best For                   |
|-----------------------|---------------------------------------------|----------------------------|
| Blank                 | Empty project                               | Custom workflows           |
| Software Development  | Backlog, Sprint, In Progress, Review, Done  | Dev teams, agile sprints   |
| Marketing Campaign    | Planning, Content, Design, Review, Published| Marketing teams            |
| Product Launch        | Research, Development, Testing, Launch       | Product managers           |
| Client Onboarding     | Kickoff, Setup, Training, Handoff           | Client-facing teams        |
| Event Planning        | Pre-Event, Logistics, Day-Of, Post-Event    | Event coordinators         |
| Bug Tracking          | Reported, Triaged, In Progress, Fixed, Closed| QA teams                  |

**Archiving a Project:**
1. Open the project
2. Click **Settings** (gear icon)
3. Click **"Archive Project"**
4. Confirm the action
5. Archived projects move to **Settings > Archived Projects**
6. Archived projects are read-only but fully searchable
7. To restore, go to Archived Projects and click **"Restore"**

**Deleting a Project:**
1. The project must be archived first
2. Go to **Settings > Archived Projects**
3. Click the **three-dot menu** on the project
4. Select **"Permanently Delete"**
5. Type the project name to confirm
6. This action is **irreversible** - all tasks, comments, and files are permanently removed

### 3.2 Tasks

**Creating a Task:**
1. Open a project
2. Click **"+ Add Task"** (or press **T** as keyboard shortcut)
3. Enter the **task title** (required)
4. Optional fields:
   - **Description**: Rich text with formatting, links, images, and code blocks
   - **Assignee**: One or more team members
   - **Due Date**: Specific date, or date range for multi-day tasks
   - **Priority**: Urgent, High, Medium, Low (default: Medium)
   - **Labels**: Color-coded tags (create custom labels in Project Settings)
   - **Estimated Time**: Hours and minutes for time tracking
   - **Attachments**: Drag-and-drop files (max 25 MB per file)
   - **Subtasks**: Break down into smaller items
   - **Dependencies**: Link tasks that must be completed first

**Task Statuses:**
Default statuses (customizable per project):
- **To Do** - Not yet started
- **In Progress** - Currently being worked on
- **In Review** - Awaiting review or approval
- **Done** - Completed
- **Blocked** - Cannot proceed (dependency or external blocker)

**Task Views:**
- **List View**: Traditional list with sortable columns
- **Kanban Board**: Drag-and-drop cards across status columns
- **Calendar View**: Tasks displayed on a calendar by due date
- **Timeline/Gantt**: Visual timeline showing task durations and dependencies
- **Table View**: Spreadsheet-style view for bulk editing

**Bulk Actions:**
Select multiple tasks (checkbox) to:
- Change status, priority, or assignee
- Add/remove labels
- Set due dates
- Move to another project
- Delete tasks

**Task Keyboard Shortcuts:**
| Shortcut    | Action                 |
|-------------|------------------------|
| T           | Create new task        |
| E           | Edit selected task     |
| D           | Set due date           |
| A           | Assign task            |
| L           | Add label              |
| P           | Change priority        |
| Ctrl/Cmd+C  | Copy task link         |
| Delete      | Move to trash          |

### 3.3 Team Collaboration

**Roles and Permissions:**

| Permission              | Admin | Manager | Member | Viewer |
|-------------------------|-------|---------|--------|--------|
| Create/delete projects  | Yes   | Yes     | No     | No     |
| Edit project settings   | Yes   | Yes     | No     | No     |
| Invite/remove members   | Yes   | Yes     | No     | No     |
| Create/edit tasks       | Yes   | Yes     | Yes    | No     |
| Comment on tasks        | Yes   | Yes     | Yes    | Yes    |
| View projects/tasks     | Yes   | Yes     | Yes    | Yes    |
| Access billing          | Yes   | No      | No     | No     |
| Manage integrations     | Yes   | Yes     | No     | No     |
| Export data             | Yes   | Yes     | Yes    | No     |
| Delete team             | Yes   | No      | No     | No     |

**Comments and Mentions:**
- Comment on any task using the comment box at the bottom of the task detail
- **@mention** team members to notify them (e.g., `@john.doe`)
- Use **#project-name** to link to a project
- Use **TASK-XXX** format to auto-link to another task
- Rich text formatting supported (bold, italic, code, lists, links)
- Edit or delete your own comments within 15 minutes of posting

**Activity Feed:**
- Every project has an activity feed showing all changes
- Filter by: task updates, comments, member changes, file uploads
- Activity is also available at the team level (Settings > Activity Log)

**Real-Time Updates:**
- All changes sync in real-time across all connected clients
- Presence indicators show who is currently viewing a task
- Typing indicators appear when someone is writing a comment

### 3.4 Reporting and Dashboards

**Built-in Reports:**
- **Project Progress**: Percentage complete, tasks by status, burndown chart
- **Team Workload**: Tasks per member, overdue items, availability
- **Time Tracking Summary**: Hours logged per project, per member, per week
- **Overdue Tasks**: List of all tasks past their due date
- **Completion Trends**: Weekly/monthly task completion rates

**Custom Dashboards:**
1. Go to **Reporting > Dashboards**
2. Click **"+ New Dashboard"**
3. Add widgets by clicking **"+ Add Widget"**:
   - Bar charts, line graphs, pie charts
   - Task counts, progress bars
   - Table views with custom filters
   - Time tracking summaries
4. Configure each widget with data source, filters, and display options
5. Arrange widgets via drag-and-drop
6. Share dashboards with team members or keep private

**Exporting Data:**
- Export any report as **CSV** or **PDF**
- Export project data including tasks, comments, and attachments
- Schedule **automated weekly/monthly reports** via email (Professional plan+)
- Go to **Reporting > Exports** to manage export history

### 3.5 Time Tracking

**Logging Time:**
1. Open a task
2. Click the **clock icon** or **"Log Time"** button
3. Enter hours and minutes manually, OR
4. Click **"Start Timer"** to track in real-time
5. Add an optional description of work performed
6. Click **"Save"**

**Timer Features:**
- Start/stop timer from task detail or the floating timer widget
- Timer persists across page navigation
- Only one timer can run at a time; starting a new timer stops the current one
- Idle detection: prompted after 15 minutes of inactivity to continue or discard

**Time Reports:**
- View time logged per project, member, or date range
- Compare estimated vs. actual time
- Export time reports as CSV for billing or invoicing

**Note:** Time tracking is available on Professional and Enterprise plans only.

---

## 4. Integrations

### 4.1 Slack Integration

**Setup:**
1. Go to **Settings > Integrations > Slack**
2. Click **"Connect to Slack"**
3. Authorize TechCorp in your Slack workspace (requires Slack admin or app install permissions)
4. Select which Slack channels to link to TechCorp projects
5. Configure notification preferences

**Slack Notifications:**
- Task created, updated, completed, or assigned
- Comments and @mentions
- Due date reminders
- Project milestones reached

**Slack Commands:**
| Command                        | Description                               |
|--------------------------------|-------------------------------------------|
| `/techcorp status`             | Show your current tasks and status         |
| `/techcorp create [task name]` | Create a new task in the default project   |
| `/techcorp list`               | List your assigned tasks                   |
| `/techcorp done [TASK-ID]`     | Mark a task as completed                   |
| `/techcorp help`               | Show available commands                    |

**Troubleshooting Slack Integration:**
- If notifications stop: Re-authorize the integration in Settings > Integrations > Slack
- If commands don't work: Ensure the TechCorp bot is invited to the channel (`/invite @TechCorp`)
- Slack permissions required: `chat:write`, `commands`, `channels:read`

### 4.2 GitHub Integration

**Setup:**
1. Go to **Settings > Integrations > GitHub**
2. Click **"Connect to GitHub"**
3. Authorize TechCorp to access your GitHub organization
4. Select which repositories to link
5. Map repositories to TechCorp projects

**Features:**
- **PR Linking**: Reference TechCorp tasks in PR titles or descriptions using `TASK-XXX` format. The task will automatically show the linked PR.
- **Auto-Updates**: When a PR is merged, linked tasks can automatically move to "Done" status (configurable)
- **Branch Creation**: Create a GitHub branch directly from a TechCorp task (branch name auto-generated from task title)
- **Commit References**: Commits referencing `TASK-XXX` appear in the task activity feed
- **Status Sync**: PR review status (approved, changes requested) reflected on the task

**Configuration Options:**
- Auto-close tasks on PR merge: On/Off (per project)
- Branch naming convention: `feature/TASK-XXX-description` or `TASK-XXX/description`
- Require task reference in PR: Warning or Block

### 4.3 Jira Integration

**Import from Jira:**
1. Go to **Settings > Integrations > Jira**
2. Click **"Import from Jira"**
3. Enter your Jira instance URL (e.g., `yourcompany.atlassian.net`)
4. Authorize TechCorp to access Jira
5. Select which Jira projects to import
6. Map Jira statuses to TechCorp statuses
7. Map Jira priority levels to TechCorp priorities
8. Review the import preview
9. Click **"Start Import"**

**Import Details:**
- Issues become Tasks; Epics become Projects (optional)
- Subtasks are preserved as subtasks
- Comments and attachments are imported (attachments up to 25 MB)
- Assignees are mapped by email address
- Import runs in background; email notification on completion
- Import can take 5-30 minutes depending on volume

**Two-Way Sync (Enterprise only):**
- Keep Jira and TechCorp in sync in real-time
- Status changes in either tool update the other
- New tasks/issues created in either tool appear in both
- Configure sync direction: TechCorp-to-Jira, Jira-to-TechCorp, or Bidirectional

### 4.4 Zapier Integration

**Setup:**
1. Log in to your Zapier account
2. Search for **"TechCorp"** in the app directory
3. Click **"Connect"** and authorize with your TechCorp API key
4. Create a new Zap with TechCorp as trigger or action

**Available Triggers:**
| Trigger                  | Fires When                              |
|--------------------------|-----------------------------------------|
| New Task Created         | A task is created in a specified project |
| Task Status Changed      | A task moves to a new status            |
| Task Assigned            | A task is assigned to a member          |
| Task Completed           | A task is marked as Done                |
| New Comment              | A comment is added to a task            |
| New Project Created      | A new project is created                |
| Due Date Approaching     | A task's due date is within X days      |

**Available Actions:**
| Action                   | Does                                     |
|--------------------------|------------------------------------------|
| Create Task              | Creates a new task in a project          |
| Update Task              | Updates task fields (status, assignee)   |
| Create Comment           | Adds a comment to a task                 |
| Create Project           | Creates a new project                    |
| Invite Member            | Sends a team invitation                  |

**Popular Zap Templates:**
- Gmail attachment -> TechCorp task with attachment
- Google Forms response -> New TechCorp task
- Slack message (with emoji reaction) -> New TechCorp task
- TechCorp task completed -> Google Sheets row

### 4.5 REST API

**Base URL:** `https://api.techcorp.io/v2`

**Authentication:**
- API key passed via `Authorization: Bearer <API_KEY>` header
- Generate API keys in **Settings > Integrations > API**
- Each key can have scoped permissions (read-only, read-write, admin)
- Keys can be revoked at any time

**Rate Limits:**
| Plan          | Requests per Minute | Requests per Day |
|---------------|--------------------:|------------------:|
| Starter       | 60                  | 5,000             |
| Professional  | 300                 | 50,000            |
| Enterprise    | 1,000               | Unlimited         |

**Key Endpoints:**

| Method | Endpoint                          | Description              |
|--------|-----------------------------------|--------------------------|
| GET    | `/projects`                       | List all projects        |
| POST   | `/projects`                       | Create a project         |
| GET    | `/projects/:id`                   | Get project details      |
| GET    | `/projects/:id/tasks`             | List tasks in a project  |
| POST   | `/projects/:id/tasks`             | Create a task            |
| GET    | `/tasks/:id`                      | Get task details         |
| PUT    | `/tasks/:id`                      | Update a task            |
| DELETE | `/tasks/:id`                      | Delete a task            |
| POST   | `/tasks/:id/comments`             | Add a comment            |
| GET    | `/team/members`                   | List team members        |
| GET    | `/time-entries`                   | List time entries        |
| POST   | `/time-entries`                   | Log time                 |
| GET    | `/webhooks`                       | List webhooks            |
| POST   | `/webhooks`                       | Create a webhook         |

**Webhooks:**
- Subscribe to events (task.created, task.updated, task.completed, comment.added, etc.)
- Webhook payloads are signed with HMAC-SHA256 for verification
- Failed deliveries are retried 3 times with exponential backoff
- Webhook logs available in **Settings > Integrations > API > Webhooks**

**Example - Create a Task:**
```json
POST /projects/proj_123/tasks
Authorization: Bearer tk_live_abc123

{
  "title": "Design new landing page",
  "description": "Create mockups for the Q2 campaign landing page",
  "assignee_id": "user_456",
  "priority": "high",
  "due_date": "2025-03-15",
  "labels": ["design", "q2-campaign"]
}
```

**Response:**
```json
{
  "id": "task_789",
  "title": "Design new landing page",
  "status": "to_do",
  "priority": "high",
  "created_at": "2025-02-20T10:30:00Z",
  "project_id": "proj_123",
  "assignee": {
    "id": "user_456",
    "name": "Jane Smith"
  }
}
```

**Error Responses:**
```json
{
  "error": {
    "code": "rate_limit_exceeded",
    "message": "You have exceeded the rate limit. Please retry after 60 seconds.",
    "retry_after": 60
  }
}
```

---

## 5. Troubleshooting

### 5.1 Login Issues

**Cannot Log In - Incorrect Password:**
1. Double-check that Caps Lock is off
2. Ensure you are using the correct email address
3. Try the **"Forgot Password?"** flow (see Section 2.1)
4. If using SSO (Enterprise), contact your IT administrator
5. Clear browser cache and cookies, then try again

**Account Locked:**
- Accounts are locked after **5 consecutive failed login attempts**
- Lockout duration: **15 minutes** (automatic unlock)
- If still locked after 15 minutes, request a password reset
- Enterprise SSO lockouts are managed by your identity provider

**SSO Issues (Enterprise):**
- Ensure your identity provider (Okta, Azure AD, Google Workspace) is configured correctly
- Check that the user's email in the IdP matches their TechCorp email
- SAML assertion must include `email` and `name` attributes
- Contact your IT admin to verify SSO configuration

**Browser-Specific Login Issues:**
- Clear browser cache and cookies for `*.techcorp.io`
- Disable browser extensions (especially ad blockers or privacy extensions)
- Try in an incognito/private window
- Update your browser to the latest version

### 5.2 Sync Errors

**Tasks Not Syncing Across Devices:**
1. Check your internet connection
2. Hard refresh the page (Ctrl+Shift+R / Cmd+Shift+R)
3. Log out and log back in
4. Check **https://status.techcorp.io** for any ongoing incidents
5. If using the mobile app, force-close and reopen

**Integration Sync Issues:**
- **Slack not syncing:** Re-authorize the integration; ensure the TechCorp bot is in the channel
- **GitHub PRs not linking:** Verify the task ID format is correct (`TASK-XXX`); check repository mapping
- **Jira sync delay:** Bidirectional sync can take up to 5 minutes; check Jira webhook status
- **Zapier triggers not firing:** Check your Zap is turned on; review Zapier task history for errors

**Offline Mode:**
- TechCorp supports limited offline functionality in the desktop and mobile apps
- Changes made offline are queued and synced when connection is restored
- Conflict resolution: Last-write-wins for field updates; comments are merged chronologically
- Offline mode does NOT support: file uploads, integration triggers, or real-time collaboration

### 5.3 Notification Problems

**Not Receiving Email Notifications:**
1. Check **Profile Settings > Notifications** to ensure email notifications are enabled
2. Verify the correct email address is listed
3. Check spam/junk folders
4. Add `notifications@techcorp.io` to your email contacts/safe senders list
5. If using a corporate email, check with IT for email filtering rules

**Not Receiving Mobile Push Notifications:**
1. Ensure push notifications are enabled in your phone's Settings for the TechCorp app
2. Check in-app notification settings (**Settings > Notifications > Mobile Push**)
3. Force-close and reopen the app
4. Ensure you are running the latest app version
5. Reinstall the app if issues persist

**Too Many Notifications:**
1. Go to **Profile Settings > Notifications**
2. Customize which events trigger notifications:
   - Assigned to me / Mentioned / All activity
3. Set **Quiet Hours** to pause notifications during specific times
4. Use **project-level notification settings** to mute specific projects
5. Use **"Watch" / "Unwatch"** on individual tasks

### 5.4 Performance Tips

**Slow Page Load:**
- Clear browser cache (Settings > Clear Browsing Data > Cached Images and Files)
- Disable unnecessary browser extensions
- Ensure minimum 5 Mbps internet connection
- Try a different browser
- If using many large attachments, consider archiving old files

**Slow Task List:**
- Projects with 1,000+ tasks may experience slower loading
- Use **filters** to narrow the view instead of scrolling all tasks
- Archive completed tasks periodically
- Use **pagination** in Table view for large datasets

**Mobile App Performance:**
- Ensure you are on the latest app version
- Clear the app cache (Settings > App > TechCorp > Clear Cache)
- Restart your device
- Uninstall and reinstall if persistent

### 5.5 Browser Compatibility

**Supported Browsers:**
| Browser          | Minimum Version | Notes                        |
|------------------|-----------------|------------------------------|
| Google Chrome    | 90+             | Recommended browser          |
| Mozilla Firefox  | 88+             | Full support                 |
| Apple Safari     | 15+             | Full support                 |
| Microsoft Edge   | 90+             | Full support (Chromium-based)|
| Opera            | 76+             | Supported                    |
| Internet Explorer| N/A             | **Not supported**            |

**Known Browser Issues:**
- Safari: Drag-and-drop in Kanban view may be laggy with 100+ cards
- Firefox: File upload dialog may not show thumbnails
- All browsers: Pop-up blockers may prevent the OAuth windows for integrations

### 5.6 File and Storage Issues

**File Upload Failures:**
- Maximum file size: **25 MB per file**
- Allowed formats: All common formats (documents, images, videos, archives)
- Blocked formats: `.exe`, `.bat`, `.cmd`, `.sh`, `.msi` (security policy)
- If upload fails, check your remaining storage quota in Settings > Billing
- Large files (>10 MB) may take longer on slow connections; do not close the browser during upload

**Storage Quota:**
- Starter: 5 GB
- Professional: 50 GB
- Enterprise: Unlimited
- View usage: **Settings > Billing > Storage**
- To free up space: delete old attachments or archive projects

---

## 6. Common Error Codes

When encountering errors in TechCorp, you may see the following error codes. Use this reference to understand and resolve them.

### ERR-001: Authentication Failed

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-001                                                |
| **Cause** | Invalid credentials, expired session, or revoked API key |
| **Solution** | 1. Re-enter your email and password. 2. Clear browser cookies for techcorp.io. 3. Reset your password if needed. 4. For API: regenerate your API key in Settings > Integrations > API. |
| **Severity** | Medium |

### ERR-002: Permission Denied

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-002                                                |
| **Cause** | User does not have the required role/permission for this action |
| **Solution** | 1. Check your role (Admin, Manager, Member, Viewer) in Settings > Team. 2. Contact your team Admin to request the necessary permissions. 3. Admins can change roles in Settings > Team Members. |
| **Severity** | Low |

### ERR-003: Resource Not Found

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-003                                                |
| **Cause** | The requested project, task, or resource does not exist or has been deleted |
| **Solution** | 1. Verify the URL or ID is correct. 2. Check if the resource was archived (Settings > Archived Projects). 3. If deleted, it cannot be recovered after 30 days. |
| **Severity** | Low |

### ERR-004: Rate Limit Exceeded

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-004                                                |
| **Cause** | Too many API requests in a short period (exceeds plan limits) |
| **Solution** | 1. Wait for the retry period indicated in the response header (`Retry-After`). 2. Implement exponential backoff in your API client. 3. Consider upgrading your plan for higher rate limits. 4. Review API usage in Settings > Integrations > API > Usage. |
| **Severity** | Medium |

### ERR-005: File Upload Failed

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-005                                                |
| **Cause** | File exceeds size limit (25 MB), unsupported format, or storage quota reached |
| **Solution** | 1. Check file size (max 25 MB). 2. Verify file format is not blocked (.exe, .bat, .cmd, .sh, .msi). 3. Check storage quota in Settings > Billing > Storage. 4. Delete old files or upgrade plan for more storage. |
| **Severity** | Low |

### ERR-006: Integration Connection Failed

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-006                                                |
| **Cause** | OAuth token expired, service unavailable, or permissions revoked |
| **Solution** | 1. Go to Settings > Integrations. 2. Disconnect the affected integration. 3. Reconnect and re-authorize. 4. Check the third-party service's status page. 5. Ensure required permissions are granted during OAuth. |
| **Severity** | Medium |

### ERR-007: Webhook Delivery Failed

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-007                                                |
| **Cause** | Webhook endpoint returned non-2xx status, timed out, or is unreachable |
| **Solution** | 1. Verify your webhook endpoint URL is correct and accessible. 2. Check your server logs for errors. 3. Ensure your endpoint responds within 10 seconds. 4. TechCorp retries failed deliveries 3 times. 5. Check webhook logs in Settings > Integrations > API > Webhooks. |
| **Severity** | Medium |

### ERR-008: Subscription Expired

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-008                                                |
| **Cause** | Payment failed and grace period expired, or subscription was cancelled |
| **Solution** | 1. Go to Settings > Billing. 2. Update payment method. 3. Retry the failed payment. 4. If cancelled, reactivate within 30 days to restore data. 5. Contact billing@techcorp.io for payment issues. |
| **Severity** | High |

### ERR-009: Data Export Failed

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-009                                                |
| **Cause** | Export job timed out (large dataset), insufficient permissions, or service error |
| **Solution** | 1. Try exporting a smaller date range or fewer projects. 2. Ensure you have at least Member role. 3. If exporting via API, use pagination. 4. Try again in a few minutes; the export service may have been temporarily overloaded. |
| **Severity** | Low |

### ERR-010: SSO Configuration Error

| Field     | Details                                                |
|-----------|--------------------------------------------------------|
| **Code**  | ERR-010                                                |
| **Cause** | SAML configuration mismatch, invalid IdP certificate, or metadata URL unreachable |
| **Solution** | 1. Verify your SAML Entity ID and ACS URL in TechCorp match your IdP settings. 2. Ensure the IdP certificate has not expired. 3. Check that the IdP metadata URL is publicly accessible. 4. Contact your IT administrator for IdP configuration. 5. Enterprise support can assist with SAML debugging. |
| **Severity** | High |

---

## 7. Frequently Asked Questions

### General

**Q: Can I use TechCorp for free?**
A: TechCorp offers a 14-day free trial on Starter and Professional plans. No credit card is required to start the trial. After the trial, you can choose a paid plan or your account will be suspended (data retained for 30 days).

**Q: Is there a limit on the number of projects?**
A: No. All plans allow unlimited projects. The limits apply to team members and storage.

**Q: Can I use TechCorp offline?**
A: The desktop and mobile apps support limited offline functionality. Changes sync automatically when you reconnect. The web app requires an active internet connection.

**Q: What happens to my data if I cancel?**
A: Your data is retained for 30 days after cancellation. You can reactivate and restore everything within that window. After 30 days, all data is permanently and irreversibly deleted.

### Billing

**Q: Can I switch between monthly and annual billing?**
A: Yes. Go to Settings > Billing > Plan and select your preferred billing cycle. If switching from monthly to annual, you receive a 20% discount and are charged the prorated annual amount.

**Q: Do you offer refunds?**
A: We offer a full refund within the first 30 days of your initial subscription. After that, we do not offer refunds, but you can cancel at any time and access continues until the end of the billing period. Contact billing@techcorp.io for refund requests.

**Q: Can I get a discount for non-profits or education?**
A: Yes, we offer 50% off for verified non-profit organizations and educational institutions. Contact sales@techcorp.io with proof of non-profit/educational status.

### Security

**Q: Is my data encrypted?**
A: Yes. All data is encrypted in transit (TLS 1.3) and at rest (AES-256). API keys are hashed and never stored in plaintext.

**Q: Where is my data stored?**
A: Data is hosted on AWS in US-East (Virginia) by default. EU customers can request data residency in AWS EU-West (Ireland). Enterprise customers can choose their data region.

**Q: Is TechCorp SOC 2 compliant?**
A: Yes, TechCorp is SOC 2 Type II certified. You can request the audit report under NDA for Enterprise evaluations.

**Q: How do I report a security vulnerability?**
A: Email security@techcorp.io with details. We follow responsible disclosure practices and acknowledge reports within 24 hours.

### Mobile App

**Q: Is the mobile app free?**
A: Yes, the mobile app is included with all plans and available on iOS and Android.

**Q: Why is the mobile app asking me to update?**
A: We require minimum app versions for security and compatibility. Update to the latest version from the App Store or Google Play.

**Q: Can I use the mobile app offline?**
A: Yes, you can view existing tasks and add new tasks offline. Changes sync when you reconnect.

---

*For issues not covered in this documentation, contact TechCorp Support:*
- **Email:** support@techcorp.io
- **WhatsApp:** +1-555-TECHCORP (+1-555-832-4267)
- **Web Form:** https://support.techcorp.io/contact
- **Knowledge Base:** https://support.techcorp.io/kb
- **Status Page:** https://status.techcorp.io
