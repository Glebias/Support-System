'use client'
import { useActionState, useEffect, useRef, useState } from 'react'
import { maxLength, minLength, pipe, string, trim, email, parse } from 'valibot'
import styles from './Registration.module.css'
import insertUser from '@/actions/User/insertUser'
import selectUsersEmail from '@/actions/User/selectUsersEmail'

const passwordSchema = pipe(
  string(),
  trim(),
  minLength(6, 'Минимальная длина пароля - 6 символов'),
  maxLength(30, 'Максимальная длина пароля - 30 символов')
)

const emailSchema = pipe(
  string(),
  trim(),
  email('Введите корректный email адрес')
)

interface Registration {
  registration: number;
  setRegistration: (registration: number) => void;
}

export default function Registration({ registration, setRegistration }: Registration) {
  const [usersEmails, setUsersEmail] = useState<string[] | undefined>()
  const modalRef = useRef<HTMLDivElement>(null)

  async function registrationAction(prevState: any, formData: FormData) {
    const email = formData.get('email') as string
  const password = formData.get('password') as string
  
  try {
    parse(emailSchema, email)
  } catch (error: any) {
    return { 
      email: formData.get('email'),
      password: formData.get('password'),
      success: false, 
      error: 'Проверьте правильность введенных данных',
      fieldErrors: { email: 'Введите корректный email адрес' }
    }
  }
  
  try {
    parse(passwordSchema, password)
  } catch (error: any) {
    return { 
      email: formData.get('email'),
      password: formData.get('password'),
      success: false, 
      error: 'Проверьте правильность введенных данных',
      fieldErrors: { password: error.message }
    }
  }
  
  if (!usersEmails || usersEmails.find(element => element === email)) {
    console.log(usersEmails)
    return { 
            email: formData.get('email'),
      password: formData.get('password'),
      success: false, 
      error: 'Этот email уже используется',
      fieldErrors: { email: 'Этот email уже используется' }
    }
  }
  insertUser({email: email, password: password})
  setRegistration(0)
  return {       email: formData.get('email'),
      password: formData.get('password'), success: true, error: null, fieldErrors: {} }
}
  const [state, action, isPending] = useActionState(registrationAction, {
    email: '',
    password: '',
    success: false,
    error: null,
    fieldErrors: {}
  })
  useEffect(() => {
    async function selectEmails() {
      const data = await selectUsersEmail()
      setUsersEmail(data)
    }
  selectEmails()
  },[])

  useEffect(() => {
    const handleEscape = (e: KeyboardEvent) => {
      if (e.key === 'Escape' && registration !== 0) {
        setRegistration(0)
      }
    }

    document.addEventListener('keydown', handleEscape)
    return () => document.removeEventListener('keydown', handleEscape)
  }, [registration, setRegistration])

  const handleOverlayClick = (e: React.MouseEvent) => {
    if (e.target === e.currentTarget) {
      setRegistration(0)
    }
  }

  const handleLoginClick = () => {
    setRegistration(2)
  }

  return (
    <section 
      className={registration === 1 ? styles.modalVisible : styles.modalUnvisible}
      onClick={handleOverlayClick}
      ref={modalRef}
    >
      <div className={styles.modalContent}>
        <form action={action} className={styles.registrationForm}>
          <div className={styles.formHeader}>
            <h2>Регистрация</h2>
            <button 
              type="button" 
              className={styles.closeButton}
              onClick={() => setRegistration(0)}
              aria-label="Закрыть регистрацию"
            >
              ×
            </button>
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="email">Email</label>
            <input
              type="email"
              id="email"
              name="email"
              placeholder="example@gmail.com"
              required
              defaultValue={typeof state.email === 'string' ? state.email : ''}
            />
            {state.fieldErrors?.email && (
              <span className={styles.errorText}>{state.fieldErrors.email}</span>
            )}
          </div>

          <div className={styles.inputGroup}>
            <label htmlFor="password">Пароль</label>
            <input
              type="password"
              id="password"
              name="password"
              placeholder="Введите пароль"
              required
              minLength={6}
              maxLength={30}
              defaultValue={typeof state.password === 'string' ? state.password : ''}
            />
            {state.fieldErrors?.password && (
              <span className={styles.errorText}>{state.fieldErrors.password}</span>
            )}
          </div>

          {state.error && !state.fieldErrors?.email && !state.fieldErrors?.password && (
            <div className={styles.formError}>{state.error}</div>
          )}

          <button 
            type="submit" 
            className={styles.submitButton}
            disabled={isPending}
          >
            {isPending ? 'Регистрация...' : 'Зарегистрироваться'}
          </button>

          <div className={styles.loginSwitch}>
            <p className={styles.p}>Уже есть аккаунт?</p>
            <button 
              type="button" 
              className={styles.loginButton}
              onClick={handleLoginClick}
            >
              Войти в аккаунт
            </button>
          </div>
        </form>
      </div>
    </section>
  )
}