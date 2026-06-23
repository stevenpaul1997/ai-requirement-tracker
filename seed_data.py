from dotenv import load_dotenv
load_dotenv()
from database.mongo_client import insert_raw_intake
from database.postgres_client import insert_requirement, insert_user_stories, update_status

reqs = [
    ('AI-Powered Customer Churn Prediction','Sales','Jennifer Walsh','C-Suite / Executive','High','Must Have','Approved'),
    ('Automated Payroll Processing System','Finance','Robert Kim','VP / Director','High','Must Have','In Development'),
    ('Employee Performance Dashboard','HR','Amanda Foster','Department Head / Manager','Medium','Should Have','Approved'),
    ('Supply Chain Real-Time Visibility Portal','Operations','Marcus Johnson','VP / Director','High','Must Have','In Development'),
    ('Customer Self-Service Knowledge Base','Customer Success','Priya Patel','Department Head / Manager','Medium','Should Have','Under Review'),
    ('Multi-Factor Authentication Rollout','IT','Daniel Chen','C-Suite / Executive','High','Must Have','Done'),
    ('Marketing Campaign Analytics Platform','Marketing','Sophie Laurent','Department Head / Manager','Medium','Should Have','Under Review'),
    ('Mobile App for Field Sales Reps','Sales','Carlos Rivera','Team Lead','Medium','Should Have','Submitted'),
    ('Vendor Contract Management System','Legal','Rachel Thompson','Department Head / Manager','Medium','Could Have','Submitted'),
    ('Internal Wiki and Documentation Portal','IT','Kevin Park','Team Lead','Medium','Could Have','Done'),
    ('Expense Report Automation','Finance','Lisa Wong','End User','Low','Could Have','Under Review'),
    ('Office Floor Plan Digital Display','Operations','Tom Bradley','End User','Low','Could Have','Submitted'),
    ('Quarterly Business Review Automation','Finance','Sarah Mitchell','C-Suite / Executive','High','Must Have','Approved'),
    ('Employee Wellness Program Portal','HR','Nina Sharma','End User','Low',"Won't Have",'Rejected'),
    ('Product Roadmap Collaboration Tool','Product','Alex Turner','VP / Director','High','Must Have','In Development'),
]

stories = [
    {'story':'As a stakeholder, I want to submit requirements so that AI generates user stories.','acceptance_criteria':'Given the form is open, When I submit, Then AI returns analysis within 10 seconds.'},
    {'story':'As a BA, I want to review AI-generated stories so that I can validate before handoff.','acceptance_criteria':'Given a requirement is submitted, When processing completes, Then 3 stories are displayed.'},
    {'story':'As a PM, I want to track status so that I have full pipeline visibility.','acceptance_criteria':'Given requirements exist, When I view tracker, Then I can filter by status and priority.'},
]

for t,dept,by,role,pri,mos,status in reqs:
    print(f'Inserting: {t}')
    mid = insert_raw_intake({'title':t,'description':t,'department':dept,'submitted_by':by,'role':role,'business_objective':'Improve business outcomes','additional_notes':''})
    rid = insert_requirement(mongo_id=mid,title=t,submitted_by=by,department=dept,role=role,priority=pri,moscow=mos)
    insert_user_stories(rid,stories)
    if status != 'Submitted':
        update_status(rid,status,'Submitted')
    print(f'  Done REQ-{rid:04d} | {status}')

print('All 15 inserted.')
