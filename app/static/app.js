// Базовый URL API
const API_BASE = '/api/v1';

// Глобальные переменные для хранения данных (для быстрого доступа)
let students = [];
let subjects = [];
let scores = [];

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', () => {
    loadAllData();
});

// Загрузка всех данных с API
async function loadAllData() {
    await Promise.all([
        loadStudents(),
        loadSubjects(),
        loadScores()
    ]);
}

// Загрузка студентов
async function loadStudents() {
    try {
        const response = await fetch(`${API_BASE}/students/`);
        students = await response.json();
        renderStudents();
    } catch (error) {
        console.error('Ошибка загрузки студентов:', error);
    }
}

// Загрузка предметов
async function loadSubjects() {
    try {
        const response = await fetch(`${API_BASE}/subjects/`);
        subjects = await response.json();
        renderSubjects();
    } catch (error) {
        console.error('Ошибка загрузки предметов:', error);
    }
}

// Загрузка оценок
async function loadScores() {
    try {
        const response = await fetch(`${API_BASE}/scores/`);
        scores = await response.json();
        renderScores();
    } catch (error) {
        console.error('Ошибка загрузки оценок:', error);
    }
}

// Отрисовка таблицы студентов
function renderStudents() {
    const tbody = document.querySelector('#studentsTable tbody');
    tbody.innerHTML = '';
    students.forEach(student => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${student.id}</td>
            <td>${student.first_name}</td>
            <td>${student.last_name}</td>
            <td>${student.email}</td>
            <td>${student.group_name || ''}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editStudent(${student.id})">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="deleteStudent(${student.id})">Удалить</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Отрисовка таблицы предметов
function renderSubjects() {
    const tbody = document.querySelector('#subjectsTable tbody');
    tbody.innerHTML = '';
    subjects.forEach(subject => {
        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${subject.id}</td>
            <td>${subject.name}</td>
            <td>${subject.description || ''}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editSubject(${subject.id})">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="deleteSubject(${subject.id})">Удалить</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Отрисовка таблицы оценок
function renderScores() {
    const tbody = document.querySelector('#scoresTable tbody');
    tbody.innerHTML = '';
    scores.forEach(score => {
        const student = students.find(s => s.id === score.student_id) || { first_name: '?', last_name: '' };
        const subject = subjects.find(s => s.id === score.subject_id) || { name: '?' };
        const studentName = `${student.first_name} ${student.last_name}`.trim() || 'Неизвестно';
        const date = new Date(score.created_at).toLocaleDateString();

        const row = document.createElement('tr');
        row.innerHTML = `
            <td>${score.id}</td>
            <td>${studentName}</td>
            <td>${subject.name}</td>
            <td>${score.score}</td>
            <td>${date}</td>
            <td>
                <button class="btn btn-sm btn-warning" onclick="editScore(${score.id})">Изменить</button>
                <button class="btn btn-sm btn-danger" onclick="deleteScore(${score.id})">Удалить</button>
            </td>
        `;
        tbody.appendChild(row);
    });
}

// Функции для работы со студентами
window.showAddStudentForm = function() {
    document.getElementById('modalTitle').innerText = 'Добавить студента';
    document.getElementById('entityId').value = '';
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Имя</label>
            <input type="text" class="form-control" id="firstName" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Фамилия</label>
            <input type="text" class="form-control" id="lastName" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" id="email" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Группа</label>
            <input type="text" class="form-control" id="groupName">
        </div>
    `;
    document.getElementById('entityForm').onsubmit = createStudent;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

window.editStudent = async function(id) {
    const student = students.find(s => s.id === id);
    if (!student) return;

    document.getElementById('modalTitle').innerText = 'Редактировать студента';
    document.getElementById('entityId').value = student.id;
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Имя</label>
            <input type="text" class="form-control" id="firstName" value="${student.first_name}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Фамилия</label>
            <input type="text" class="form-control" id="lastName" value="${student.last_name}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Email</label>
            <input type="email" class="form-control" id="email" value="${student.email}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Группа</label>
            <input type="text" class="form-control" id="groupName" value="${student.group_name || ''}">
        </div>
    `;
    document.getElementById('entityForm').onsubmit = updateStudent;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

async function createStudent(event) {
    event.preventDefault();
    const data = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        group_name: document.getElementById('groupName').value || null
    };
    try {
        const response = await fetch(`${API_BASE}/students/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Ошибка создания');
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadStudents();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function updateStudent(event) {
    event.preventDefault();
    const id = document.getElementById('entityId').value;
    const data = {
        first_name: document.getElementById('firstName').value,
        last_name: document.getElementById('lastName').value,
        email: document.getElementById('email').value,
        group_name: document.getElementById('groupName').value || null
    };
    try {
        const response = await fetch(`${API_BASE}/students/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Ошибка обновления');
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadStudents();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

window.deleteStudent = async function(id) {
    if (!confirm('Удалить студента?')) return;
    try {
        await fetch(`${API_BASE}/students/${id}`, { method: 'DELETE' });
        await loadStudents();
    } catch (error) {
        alert('Ошибка удаления');
    }
};

// Функции для работы с предметами
window.showAddSubjectForm = function() {
    document.getElementById('modalTitle').innerText = 'Добавить предмет';
    document.getElementById('entityId').value = '';
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Название</label>
            <input type="text" class="form-control" id="name" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea class="form-control" id="description"></textarea>
        </div>
    `;
    document.getElementById('entityForm').onsubmit = createSubject;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

window.editSubject = async function(id) {
    const subject = subjects.find(s => s.id === id);
    if (!subject) return;

    document.getElementById('modalTitle').innerText = 'Редактировать предмет';
    document.getElementById('entityId').value = subject.id;
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Название</label>
            <input type="text" class="form-control" id="name" value="${subject.name}" required>
        </div>
        <div class="mb-3">
            <label class="form-label">Описание</label>
            <textarea class="form-control" id="description">${subject.description || ''}</textarea>
        </div>
    `;
    document.getElementById('entityForm').onsubmit = updateSubject;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

async function createSubject(event) {
    event.preventDefault();
    const data = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value || null
    };
    try {
        const response = await fetch(`${API_BASE}/subjects/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Ошибка создания');
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadSubjects();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function updateSubject(event) {
    event.preventDefault();
    const id = document.getElementById('entityId').value;
    const data = {
        name: document.getElementById('name').value,
        description: document.getElementById('description').value || null
    };
    try {
        const response = await fetch(`${API_BASE}/subjects/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Ошибка обновления');
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadSubjects();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

window.deleteSubject = async function(id) {
    if (!confirm('Удалить предмет?')) return;
    try {
        await fetch(`${API_BASE}/subjects/${id}`, { method: 'DELETE' });
        await loadSubjects();
    } catch (error) {
        alert('Ошибка удаления');
    }
};

// Функции для работы с оценками
window.showAddScoreForm = function() {
    let studentOptions = '<option value="">Выберите студента</option>';
    students.forEach(s => studentOptions += `<option value="${s.id}">${s.first_name} ${s.last_name}</option>`);

    let subjectOptions = '<option value="">Выберите предмет</option>';
    subjects.forEach(s => subjectOptions += `<option value="${s.id}">${s.name}</option>`);

    document.getElementById('modalTitle').innerText = 'Добавить оценку';
    document.getElementById('entityId').value = '';
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Студент</label>
            <select class="form-select" id="studentId" required>${studentOptions}</select>
        </div>
        <div class="mb-3">
            <label class="form-label">Предмет</label>
            <select class="form-select" id="subjectId" required>${subjectOptions}</select>
        </div>
        <div class="mb-3">
            <label class="form-label">Оценка (0-100)</label>
            <input type="number" class="form-control" id="score" min="0" max="100" step="0.1" required>
        </div>
    `;
    document.getElementById('entityForm').onsubmit = createScore;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

window.editScore = async function(id) {
    const score = scores.find(s => s.id === id);
    if (!score) return;

    let studentOptions = '<option value="">Выберите студента</option>';
    students.forEach(s => {
        const selected = (s.id === score.student_id) ? 'selected' : '';
        studentOptions += `<option value="${s.id}" ${selected}>${s.first_name} ${s.last_name}</option>`;
    });

    let subjectOptions = '<option value="">Выберите предмет</option>';
    subjects.forEach(s => {
        const selected = (s.id === score.subject_id) ? 'selected' : '';
        subjectOptions += `<option value="${s.id}" ${selected}>${s.name}</option>`;
    });

    document.getElementById('modalTitle').innerText = 'Редактировать оценку';
    document.getElementById('entityId').value = score.id;
    document.getElementById('formFields').innerHTML = `
        <div class="mb-3">
            <label class="form-label">Студент</label>
            <select class="form-select" id="studentId" required>${studentOptions}</select>
        </div>
        <div class="mb-3">
            <label class="form-label">Предмет</label>
            <select class="form-select" id="subjectId" required>${subjectOptions}</select>
        </div>
        <div class="mb-3">
            <label class="form-label">Оценка (0-100)</label>
            <input type="number" class="form-control" id="score" value="${score.score}" min="0" max="100" step="0.1" required>
        </div>
    `;
    document.getElementById('entityForm').onsubmit = updateScore;
    new bootstrap.Modal(document.getElementById('formModal')).show();
};

async function createScore(event) {
    event.preventDefault();
    const data = {
        student_id: parseInt(document.getElementById('studentId').value),
        subject_id: parseInt(document.getElementById('subjectId').value),
        score: parseFloat(document.getElementById('score').value)
    };
    try {
        const response = await fetch(`${API_BASE}/scores/`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || 'Ошибка создания');
        }
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadScores();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

async function updateScore(event) {
    event.preventDefault();
    const id = document.getElementById('entityId').value;
    const data = {
        score: parseFloat(document.getElementById('score').value)
    };
    try {
        const response = await fetch(`${API_BASE}/scores/${id}`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        if (!response.ok) throw new Error('Ошибка обновления');
        bootstrap.Modal.getInstance(document.getElementById('formModal')).hide();
        await loadScores();
    } catch (error) {
        alert('Ошибка: ' + error.message);
    }
}

window.deleteScore = async function(id) {
    if (!confirm('Удалить оценку?')) return;
    try {
        await fetch(`${API_BASE}/scores/${id}`, { method: 'DELETE' });
        await loadScores();
    } catch (error) {
        alert('Ошибка удаления');
    }
};