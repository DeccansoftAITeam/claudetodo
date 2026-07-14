import { useEffect, useRef, useState } from 'react'
import './App.css'

const MAX_TEXT = 255

/**
 * Tiny fetch wrapper for the /api endpoints.
 * Throws an Error with the server's detail message on a non-ok response.
 */
async function api(path, { method, body } = {}) {
  const res = await fetch(path, {
    method,
    headers: body ? { 'Content-Type': 'application/json' } : undefined,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (!res.ok) {
    let detail = `${res.status} ${res.statusText}`
    try {
      const err = await res.json()
      if (err?.detail) detail = typeof err.detail === 'string' ? err.detail : JSON.stringify(err.detail)
    } catch {
      /* response had no JSON body */
    }
    throw new Error(detail)
  }
  if (res.status === 204) return null
  return res.json()
}

function App() {
  const [todos, setTodos] = useState([])
  const [draft, setDraft] = useState('')
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(true)
  const inputRef = useRef(null)

  // Load the current todo list from the backend on mount (F5 / acceptance #5).
  useEffect(() => {
    let alive = true
    api('/api/todos')
      .then((data) => {
        if (alive) setTodos(data)
      })
      .catch((e) => {
        if (alive) setError(`Could not load todos: ${e.message}`)
      })
      .finally(() => {
        if (alive) setLoading(false)
      })
    return () => {
      alive = false
    }
  }, [])

  function validate(text) {
    const trimmed = text.trim()
    if (!trimmed) return 'Todo cannot be empty.'
    if (trimmed.length > MAX_TEXT) return `Todo must be ${MAX_TEXT} characters or fewer.`
    return ''
  }

  async function addTodo(e) {
    e.preventDefault()
    const text = draft
    const msg = validate(text)
    if (msg) {
      setError(msg)
      return
    }
    // No network call on empty/whitespace submission (acceptance #4).
    setError('')
    try {
      const created = await api('/api/todos', { method: 'POST', body: { text: text.trim() } })
      setTodos((prev) => [created, ...prev])
      setDraft('')
      inputRef.current?.focus()
    } catch (err) {
      setError(err.message)
    }
  }

  // Optimistic toggle; reconcile against server response (UX guideline).
  async function toggleTodo(todo) {
    const completed = !todo.completed
    setTodos((prev) => prev.map((t) => (t.id === todo.id ? { ...t, completed } : t)))
    try {
      const updated = await api(`/api/todos/${todo.id}`, { method: 'PATCH', body: { completed } })
      setTodos((prev) => prev.map((t) => (t.id === updated.id ? updated : t)))
    } catch (err) {
      // Revert on failure.
      setTodos((prev) => prev.map((t) => (t.id === todo.id ? { ...t, completed: todo.completed } : t)))
      setError(err.message)
    }
  }

  // Optimistic delete; reconcile against 204 response (UX guideline).
  async function deleteTodo(todo) {
    const snapshot = todos
    setTodos((prev) => prev.filter((t) => t.id !== todo.id))
    try {
      await api(`/api/todos/${todo.id}`, { method: 'DELETE' })
    } catch (err) {
      setTodos(snapshot)
      setError(err.message)
    }
  }

  const remaining = todos.filter((t) => !t.completed).length

  return (
    <div className="app">
      <header className="app__header">
        <h1>ClaudeTodo</h1>
        <p className="app__sub">
          {loading ? 'Loading…' : `${remaining} of ${todos.length} remaining`}
        </p>
      </header>

      <form className="add-form" onSubmit={addTodo}>
        <input
          ref={inputRef}
          className="add-form__input"
          type="text"
          value={draft}
          placeholder="What needs to be done?"
          maxLength={MAX_TEXT}
          onChange={(e) => setDraft(e.target.value)}
          autoFocus
        />
        <button type="submit" className="add-form__btn">
          Add
        </button>
      </form>

      {error && <p className="error" role="alert">{error}</p>}

      <ul className="todo-list">
        {todos.map((todo) => (
          <li key={todo.id} className={`todo ${todo.completed ? 'todo--done' : ''}`}>
            <label className="todo__main">
              <input
                type="checkbox"
                className="todo__check"
                checked={todo.completed}
                onChange={() => toggleTodo(todo)}
              />
              <span className="todo__text">{todo.text}</span>
            </label>
            <button
              type="button"
              className="todo__delete"
              aria-label={`Delete: ${todo.text}`}
              onClick={() => deleteTodo(todo)}
            >
              ✕
            </button>
          </li>
        ))}
        {!loading && todos.length === 0 && <li className="todo-list__empty">Nothing here yet. Add your first todo above.</li>}
      </ul>
    </div>
  )
}

export default App