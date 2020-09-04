# SafetyNet

## Project 3: Python and Data Centric Development

### Context
In the all industries, safety is paramount in making sure that the employees can work with a peace of mind and operations can run smoothly. This is especially crucial in heavy industries where the nature of the jobs are dangerous and no safety plan can completely eliminates all risk. Hence, having a strong reporting culture will educate and inform employees to do their work in a safe manner. 

This reports are meant for:
- Accident, defined as unexpected and undesirable event, especially one resulting in damage or harm. 
- Near miss, defined as an unplanned event that has the potential to cause, but does not actually result in injuryn or damage.
- Violation, defined as an action that breaks or acts against something, especially a law.

However, most reports are done via Microsoft word or excel document and this makes it inefficient to extract and retrieve data.

SafetyNet is meant for employees working in a company to upload safety reports that they see in their workplace. With SafetyNet, these reports can be directly be uploaded direct to the company database. All personnel can read the reports on the various safety issues and but only those registered can edit or delete their reports. This will empower employees to take action in reporting and be responisble for their own safety.

Website can be accessed via this link: https://fa-safetynet.herokuapp.com

Demo account:

Login: demo@safety.net

Password: demo123

## UI/UX

### Strategy
User Stories:

- As an Employee, I would like to be able to view reports on any safety violations in my company so as not to make the same mistake.

- As an Employee, I would like to complete the safety reports quickly with adequate information without having to go through a lengthy form.

- As a Safety officer, I would like to get a concise safety report so that I can quickly understand the situation and react swiftly.

- As a Safety officer, I would like to have direct updates on safety reports to be able to correct or help the situation.

### Features
#### Flask Login
With FLask Login, users have to sign up and login to their accounts to be able to create, update or delete reports. If the users are not login, they would still be able to view the reports. However, buttons allowing the user to create, update and delete will not be shown. There will be validations for the login which requires it to be in an email format as well as the password have to be 6 characters long.

#### Form Validation
All forms will have validations to ensure that respective information is collected. This is to ensure that the necessary information required is sufficient to provide a complete picture of the safety situation at the time of report. The date is set to .now() to prevent any gaming of the reports as the safety report has to be completed as soon as possible.

#### Picture Upload
A picture tells a thousand words and having one in the report will give the user a better grasp of the situation. Therefore, users are able to upload pictures on the create and update forms but it is not a compulsory requirement as in the heat of an emergency it may not be ideal to take a photo before saving oneself.

#### Search Functions
For safety officers, there is only 1 search fucntion which is by their name. For the safety reports, there will be 2 types of search functions. The global search which is located at the navbar allows the user to search any content within the respective reports. The category search allows the user to narrow down their search to location, accident type, violation type or injury.

### Features Left to Implement
- User profile
- Administrator account
- Pagination
- Password verification
- Statistics of reports by accident types, violation types
