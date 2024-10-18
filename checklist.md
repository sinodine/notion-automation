


# Admin action filter

# Admin action BO Check

# Admin action Create CustomApplicationConfigurations

## Main steps

### Step 1: Trigger admin action

- select folder zip
- company ID

### Step 2: BO Check

- BO check
- no already created app

### Step 3: Query Notion

- fetch Notion block
- extract & clean data
- perform basic checks
    - Card in the right step
    - all needed data check

### Step 4: Create object

- inject notion data in form
- add images
- check form

### Step 5: Log

- update block status
- add comment "Django config created"
- send list of activities/workshops/appointments titles (for online term checks) -> slack dm


## Error handling and edge cases

- notion page not answering
- field changes name = cannot extra field data
- two block with same company id
- no block found
- import folder issues (format)
- one of the field extracted not matching format (validators)
- Card not in the right step
- missing mandatory fields

- missing logo
- already app created
- not enought objects in BO visible
- Online terms

- issue with image screenshot
- missing screenshots
- missing logo

- error raised by form

## Warnings

- missing optionnal fields => warning
- Online terms

