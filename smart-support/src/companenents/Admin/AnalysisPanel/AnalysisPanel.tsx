'use client'
import { useState } from 'react'
import styles from './AnalysisPanel.module.css'

interface AnalysisPanelProps {
  accentColor: string
  onRunAnalysis: () => Promise<AnalysisResult>
  isAnalysisDisabled?: boolean
  initialExpanded?: boolean
}

interface AnalysisResult {
  score: number
  offered_responce: string
  main_category: string
  sub_category: string
}

export default function AnalysisPanel({
  accentColor,
  onRunAnalysis,
  isAnalysisDisabled = false,
  initialExpanded = true
}: AnalysisPanelProps) {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [isExpanded, setIsExpanded] = useState<boolean>(initialExpanded)
  const [isLoading, setIsLoading] = useState<boolean>(false)
  const [error, setError] = useState<string>('')

  const handleRunAnalysis = async () => {
    setIsLoading(true)
    setError('')
    try {
      const result = await onRunAnalysis()
      setAnalysisResult(result)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Произошла ошибка при анализе')
    } finally {
      setIsLoading(false)
    }
  }

  const handleCopyText = () => {
    if (analysisResult?.offered_responce) {
      navigator.clipboard.writeText(analysisResult.offered_responce)
        .then(() => {
          console.log('Текст скопирован!')
        })
        .catch(err => {
          console.error('Ошибка копирования:', err)
        })
    }
  }

  const togglePanel = () => {
    setIsExpanded(!isExpanded)
  }

  // Форматирование score в проценты
  const formatScore = (score: number): string => {
    return `${(score * 100).toFixed(1)}%`
  }

  return (
    <div className={`${styles.analysisPanel} ${isExpanded ? styles.expanded : styles.collapsed}`}>
      <div className={styles.panelHeader}>
        <button 
          className={styles.toggleButton}
          onClick={togglePanel}
          title={isExpanded ? "Свернуть панель" : "Развернуть панель"}
        >
          {isExpanded 
          ? <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill={accentColor} viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm45.66-93.66a8,8,0,0,1,0,11.32l-32,32a8,8,0,0,1-11.32-11.32L148.69,136H88a8,8,0,0,1,0-16h60.69l-18.35-18.34a8,8,0,0,1,11.32-11.32Z"></path></svg>
          : <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" fill={accentColor} viewBox="0 0 256 256"><path d="M128,24A104,104,0,1,0,232,128,104.11,104.11,0,0,0,128,24Zm0,192a88,88,0,1,1,88-88A88.1,88.1,0,0,1,128,216Zm48-88a8,8,0,0,1-8,8H107.31l18.35,18.34a8,8,0,0,1-11.32,11.32l-32-32a8,8,0,0,1,0-11.32l32-32a8,8,0,0,1,11.32,11.32L107.31,120H168A8,8,0,0,1,176,128Z"></path></svg>}
        </button>
        
        {isExpanded && (
          <button 
            className={styles.analyzeButton}
            onClick={handleRunAnalysis}
            disabled={isLoading || isAnalysisDisabled}
            style={{ backgroundColor: accentColor }}
          >
            {isLoading ? 'Загрузка...' : 'Загрузить анализ'}
          </button>
        )}
      </div>
      
      {isExpanded && (
        <div className={styles.analysisContent}>
          {error ? (
            <div className={styles.error}>
              {error}
            </div>
          ) : analysisResult ? (
            <div 
              className={styles.analysisResult}
              onClick={handleCopyText}
              title="Нажмите чтобы скопировать ответ"
            >
              <div className={styles.scoreSection}>
                <div className={styles.scoreLabel}>Точность совпадения:</div>
                <div 
                  className={styles.scoreValue}
                  style={{ color: accentColor }}
                >
                  {formatScore(analysisResult.score)}
                </div>
              </div>
              
              <div className={styles.categorySection}>
                <div className={styles.categoryItem}>
                  <span className={styles.categoryLabel}>Основная категория:</span>
                  <span className={styles.categoryValue}>{analysisResult.main_category}</span>
                </div>
                <div className={styles.categoryItem}>
                  <span className={styles.categoryLabel}>Подкатегория:</span>
                  <span className={styles.categoryValue}>{analysisResult.sub_category}</span>
                </div>
              </div>
              
              <div className={styles.answerSection}>
                <div className={styles.answerLabel}>Предложенный ответ:</div>
                <div className={styles.answerText}>{analysisResult.offered_responce}</div>
              </div>
            </div>
          ) : (
            <div className={styles.analysisPlaceholder}>
              {isLoading ? 'Анализ выполняется...' : 'Результат анализа появится здесь'}
            </div>
          )}
        </div>
      )}
    </div>
  )
}