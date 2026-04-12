import httpx
from behave import given, when, then

BASE_URL = "http://127.0.0.1:8000/api/v1"

# Storage for data between steps
context_data = {}


@given('существует студент с email "{email}" и именем "{name}"')
def step_create_student(context, email, name):
    """Creates a student for subsequent tests"""
    try:
        # Split name into first_name and last_name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Фамилия"

        response = httpx.post(
            f"{BASE_URL}/students/",
            json={"first_name": first_name, "last_name": last_name, "email": email}
        )
        # Store the response even if it fails (e.g., duplicate)
        context_data['existing_student_email'] = email
        context_data['existing_student_name'] = name
        if response.status_code in [200, 201]:
            context_data['existing_student_id'] = response.json().get('id')
        else:
            # If creation failed, try to find existing student
            students_response = httpx.get(f"{BASE_URL}/students/")
            if students_response.status_code == 200:
                students = students_response.json()
                for student in students:
                    if student.get('email') == email:
                        context_data['existing_student_id'] = student.get('id')
                        break
    except Exception as e:
        context.error = f"Failed to create student: {e}"
        raise


@when('я пытаюсь создать студента с тем же email "{email}" и именем "{name}"')
def step_try_create_duplicate_student(context, email, name):
    """Tries to create a student with duplicate email"""
    try:
        # Split name into first_name and last_name
        name_parts = name.split(' ', 1)
        first_name = name_parts[0]
        last_name = name_parts[1] if len(name_parts) > 1 else "Фамилия"

        response = httpx.post(
            f"{BASE_URL}/students/",
            json={"first_name": first_name, "last_name": last_name, "email": email}
        )
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to create duplicate student: {e}"
        raise


@when('я запрашиваю студента с несуществующим ID {student_id:d}')
def step_get_nonexistent_student(context, student_id):
    """Requests a non-existent student"""
    try:
        response = httpx.get(f"{BASE_URL}/students/{student_id}")
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to get student: {e}"
        raise


@given('существует дисциплина с названием "{name}" и описанием "{description}"')
def step_create_subject(context, name, description):
    """Creates a subject for subsequent tests"""
    try:
        response = httpx.post(
            f"{BASE_URL}/subjects/",
            json={"name": name, "description": description}
        )
        # Store the response even if it fails (e.g., duplicate)
        context_data['existing_subject_name'] = name
        context_data['existing_subject_description'] = description
        if response.status_code in [200, 201]:
            context_data['existing_subject_id'] = response.json().get('id')
        else:
            # If creation failed, try to find existing subject
            subjects_response = httpx.get(f"{BASE_URL}/subjects/")
            if subjects_response.status_code == 200:
                subjects = subjects_response.json()
                for subject in subjects:
                    if subject.get('name') == name:
                        context_data['existing_subject_id'] = subject.get('id')
                        break
    except Exception as e:
        context.error = f"Failed to create subject: {e}"
        raise


@when('я пытаюсь создать дисциплину с тем же названием "{name}" и описанием "{description}"')
def step_try_create_duplicate_subject(context, name, description):
    """Tries to create a subject with duplicate name"""
    try:
        response = httpx.post(
            f"{BASE_URL}/subjects/",
            json={"name": name, "description": description}
        )
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to create duplicate subject: {e}"
        raise


@when('я запрашиваю дисциплину с несуществующим ID {subject_id:d}')
def step_get_nonexistent_subject(context, subject_id):
    """Requests a non-existent subject"""
    try:
        response = httpx.get(f"{BASE_URL}/subjects/{subject_id}")
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to get subject: {e}"
        raise


@given('у студента уже есть оценка по этой дисциплине со значением {score_value:d}')
def step_create_existing_score(context, score_value):
    """Creates a score for the student for the subject"""
    try:
        student_email = context_data.get('existing_student_email', 'score_student@test.com')
        subject_name = context_data.get('existing_subject_name', 'Физика')

        # Get student ID by email if not already present
        if 'existing_student_id' not in context_data or not context_data['existing_student_id']:
            # Find student or create new one
            students_response = httpx.get(f"{BASE_URL}/students/")
            if students_response.status_code == 200:
                students = students_response.json()
                student_id = None
                for student in students:
                    if student.get('email') == student_email:
                        student_id = student.get('id')
                        break

                if not student_id:
                    create_response = httpx.post(
                        f"{BASE_URL}/students/",
                        json={"name": "Студент для оценок", "email": student_email}
                    )
                    if create_response.status_code in [200, 201]:
                        student_id = create_response.json().get('id')

                if student_id:
                    context_data['existing_student_id'] = student_id

        # Get subject ID by name if not already present
        if 'existing_subject_id' not in context_data or not context_data['existing_subject_id']:
            subjects_response = httpx.get(f"{BASE_URL}/subjects/")
            if subjects_response.status_code == 200:
                subjects = subjects_response.json()
                subject_id = None
                for subject in subjects:
                    if subject.get('name') == subject_name:
                        subject_id = subject.get('id')
                        break

                if not subject_id:
                    create_response = httpx.post(
                        f"{BASE_URL}/subjects/",
                        json={"name": subject_name, "description": "Дисциплина для теста оценок"}
                    )
                    if create_response.status_code in [200, 201]:
                        subject_id = create_response.json().get('id')

                if subject_id:
                    context_data['existing_subject_id'] = subject_id

        # Create score if we have both IDs
        if 'existing_student_id' in context_data and 'existing_subject_id' in context_data:
            response = httpx.post(
                f"{BASE_URL}/scores/",
                json={
                    "student_id": context_data['existing_student_id'],
                    "subject_id": context_data['existing_subject_id'],
                    "score": score_value
                }
            )
            if response.status_code in [200, 201]:
                context_data['existing_score'] = response.json()
            elif response.status_code == 400:
                # score might already exist, that's ok for this test
                pass
    except Exception as e:
        context.error = f"Failed to create existing score: {e}"
        raise


@when('я пытаюсь создать еще одну оценку для того же студента и дисциплины со значением {score_value:d}')
def step_try_create_duplicate_score(context, score_value):
    """Tries to create a duplicate score"""
    try:
        response = httpx.post(
            f"{BASE_URL}/scores/",
            json={
                "student_id": context_data.get('existing_student_id'),
                "subject_id": context_data.get('existing_subject_id'),
                "score": score_value
            }
        )
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to create duplicate score: {e}"
        raise


@when('я запрашиваю оценку с несуществующим ID {score_id:d}')
def step_get_nonexistent_score(context, score_id):
    """Requests a non-existent score"""
    try:
        response = httpx.get(f"{BASE_URL}/scores/{score_id}")
        context_data['last_response'] = response
    except Exception as e:
        context.error = f"Failed to get score: {e}"
        raise


@then('я получаю ошибку {status_code:d}')
def step_check_error_status(context, status_code):
    """Checks error status code"""
    response = context_data.get('last_response')
    assert response is not None, "No response received"
    assert response.status_code == status_code, \
        f"Expected status {status_code}, got {response.status_code}. Response: {response.text}"


@then('сообщение об ошибке содержит "{message}"')
def step_check_error_message(context, message):
    """Checks error message content"""
    response = context_data.get('last_response')
    assert response is not None, "No response received"

    try:
        error_data = response.json()
        error_message = str(error_data).lower()
        assert message.lower() in error_message, \
            f"Message '{error_data}' does not contain '{message}'"
    except Exception as e:
        raise AssertionError(f"Failed to parse error message: {e}. Response text: {response.text}")