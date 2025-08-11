document.addEventListener('DOMContentLoaded', function() {
  // Elements
  const prevBtn = document.getElementById('prev-btn');
  const nextBtn = document.getElementById('next-btn');
  const submitBtn = document.getElementById('submit-btn');
  const retakeBtn = document.getElementById('retake-btn');
  const progressBar = document.getElementById('questionnaire-progress');
  const currentQuestionEl = document.getElementById('current-question');
  const totalQuestionsEl = document.getElementById('total-questions');
  
  // Sections
  const physicalSection = document.getElementById('physical-section');
  const mentalSection = document.getElementById('mental-section');
  const resultsSection = document.getElementById('results-section');
  
  // Results elements
  const predominantDoshaEl = document.getElementById('predominant-dosha');
  const doshaDescriptionEl = document.getElementById('dosha-description');
  const dietRecommendationsEl = document.getElementById('diet-recommendations');
  const lifestyleRecommendationsEl = document.getElementById('lifestyle-recommendations');
  const herbRecommendationsEl = document.getElementById('herb-recommendations');
  
  // State
  let currentSection = 'physical';
  let doshaChart = null;
  
  // Question counts
  const physicalQuestions = physicalSection.querySelectorAll('.question-card').length;
  const mentalQuestions = mentalSection.querySelectorAll('.question-card').length;
  const totalQuestions = physicalQuestions + mentalQuestions;
  
  // Update total questions display
  totalQuestionsEl.textContent = totalQuestions;
  
  // Navigation functions
  function goToNextSection() {
    if (currentSection === 'physical') {
      // Check if all physical questions are answered
      const physicalAnswered = Array.from(physicalSection.querySelectorAll('.question-card')).every(card => {
        const name = card.dataset.question;
        return document.querySelector(`input[name="${name}"]:checked`);
      });
      
      if (!physicalAnswered) {
        alert('Please answer all questions in this section before proceeding.');
        return;
      }
      
      // Switch to mental section
      physicalSection.style.display = 'none';
      mentalSection.style.display = 'block';
      currentSection = 'mental';
      
      // Update progress
      currentQuestionEl.textContent = physicalQuestions + 1;
      progressBar.style.width = `${(physicalQuestions / totalQuestions) * 100}%`;
      
      // Enable previous button
      prevBtn.disabled = false;
      
      // Show submit button if all mental questions are already answered
      const mentalAnswered = Array.from(mentalSection.querySelectorAll('.question-card')).every(card => {
        const name = card.dataset.question;
        return document.querySelector(`input[name="${name}"]:checked`);
      });
      
      if (mentalAnswered) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
      }
    }
  }
  
  function goToPrevSection() {
    if (currentSection === 'mental') {
      // Switch to physical section
      mentalSection.style.display = 'none';
      physicalSection.style.display = 'block';
      currentSection = 'physical';
      
      // Update progress
      currentQuestionEl.textContent = 1;
      progressBar.style.width = '0%';
      
      // Disable previous button if at first section
      prevBtn.disabled = true;
      
      // Hide submit button, show next button
      submitBtn.style.display = 'none';
      nextBtn.style.display = 'block';
    }
  }
  
  function submitQuestionnaire() {
    // Check if all mental questions are answered
    const mentalAnswered = Array.from(mentalSection.querySelectorAll('.question-card')).every(card => {
      const name = card.dataset.question;
      return document.querySelector(`input[name="${name}"]:checked`);
    });
    
    if (!mentalAnswered) {
      alert('Please answer all questions in this section before proceeding.');
      return;
    }
    
    // Collect all responses
    const responses = {};
    document.querySelectorAll('input[type="radio"]:checked').forEach(input => {
      responses[input.name] = input.value;
    });
    
    // Send to server for analysis
    fetch('/api/dosha-analysis', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ responses }),
    })
    .then(response => response.json())
    .then(data => {
      if (data.status === 'success') {
        displayResults(data);
      } else {
        alert('Error analyzing dosha: ' + data.message);
      }
    })
    .catch(error => {
      console.error('Error:', error);
      alert('An error occurred while analyzing your dosha. Please try again.');
    });
  }
  
  function displayResults(data) {
    // Hide questionnaire sections, show results
    physicalSection.style.display = 'none';
    mentalSection.style.display = 'none';
    resultsSection.style.display = 'block';
    
    // Hide navigation buttons
    prevBtn.style.display = 'none';
    nextBtn.style.display = 'none';
    submitBtn.style.display = 'none';
    
    // Update progress bar to 100%
    progressBar.style.width = '100%';
    
    // Display predominant dosha
    predominantDoshaEl.textContent = formatDoshaName(data.dosha_type);
    
    // Display dosha description
    let descriptionHtml = '';
    if (data.dosha_info.primary) {
      descriptionHtml += `<p><strong>${data.dosha_info.primary.name} Dosha:</strong> ${data.dosha_info.primary.description}</p>`;
      descriptionHtml += `<p><strong>When balanced:</strong> ${data.dosha_info.primary.balanced_state}</p>`;
      descriptionHtml += `<p><strong>When imbalanced:</strong> ${data.dosha_info.primary.imbalanced_state}</p>`;
    }
    
    if (data.dosha_info.secondary) {
      descriptionHtml += `<hr>`;
      descriptionHtml += `<p><strong>${data.dosha_info.secondary.name} Dosha (Secondary):</strong> ${data.dosha_info.secondary.description}</p>`;
    }
    
    doshaDescriptionEl.innerHTML = descriptionHtml;
    
    // Display recommendations
    displayRecommendationList(dietRecommendationsEl, data.recommendations.diet);
    displayRecommendationList(lifestyleRecommendationsEl, data.recommendations.lifestyle);
    displayRecommendationList(herbRecommendationsEl, data.recommendations.herbs);
    
    // Create dosha chart
    createDoshaChart(data.counts);
  }
  
  function displayRecommendationList(element, items) {
    element.innerHTML = '';
    items.forEach(item => {
      const li = document.createElement('li');
      li.textContent = item;
      element.appendChild(li);
    });
  }
  
  function formatDoshaName(doshaType) {
    if (doshaType.includes('-')) {
      const [primary, secondary] = doshaType.split('-');
      return `${capitalizeFirstLetter(primary)}-${capitalizeFirstLetter(secondary)}`;
    }
    return capitalizeFirstLetter(doshaType);
  }
  
  function capitalizeFirstLetter(string) {
    return string.charAt(0).toUpperCase() + string.slice(1);
  }
  
  function createDoshaChart(counts) {
    const ctx = document.getElementById('dosha-chart').getContext('2d');
    
    // Destroy existing chart if it exists
    if (doshaChart) {
      doshaChart.destroy();
    }
    
    // Create new chart
    doshaChart = new Chart(ctx, {
      type: 'polarArea',
      data: {
        labels: ['Vata', 'Pitta', 'Kapha'],
        datasets: [{
          data: [counts.vata, counts.pitta, counts.kapha],
          backgroundColor: [
            'rgba(121, 134, 203, 0.7)',  // Vata
            'rgba(239, 83, 80, 0.7)',    // Pitta
            'rgba(102, 187, 106, 0.7)'   // Kapha
          ],
          borderColor: [
            'rgba(121, 134, 203, 1)',
            'rgba(239, 83, 80, 1)',
            'rgba(102, 187, 106, 1)'
          ],
          borderWidth: 1
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
          },
          tooltip: {
            callbacks: {
              label: function(context) {
                const label = context.label || '';
                const value = context.raw || 0;
                const total = context.dataset.data.reduce((a, b) => a + b, 0);
                const percentage = Math.round((value / total) * 100);
                return `${label}: ${percentage}%`;
              }
            }
          }
        }
      }
    });
  }
  
  // Event listeners for mental section questions
  mentalSection.querySelectorAll('input[type="radio"]').forEach(input => {
    input.addEventListener('change', () => {
      // Check if all mental questions are answered
      const mentalAnswered = Array.from(mentalSection.querySelectorAll('.question-card')).every(card => {
        const name = card.dataset.question;
        return document.querySelector(`input[name="${name}"]:checked`);
      });
      
      if (mentalAnswered) {
        nextBtn.style.display = 'none';
        submitBtn.style.display = 'block';
      }
    });
  });
  
  // Button event listeners
  prevBtn.addEventListener('click', goToPrevSection);
  nextBtn.addEventListener('click', goToNextSection);
  submitBtn.addEventListener('click', submitQuestionnaire);
  
  // Retake button
  retakeBtn.addEventListener('click', () => {
    // Reset form
    document.getElementById('dosha-form').reset();
    
    // Reset UI
    resultsSection.style.display = 'none';
    physicalSection.style.display = 'block';
    mentalSection.style.display = 'none';
    
    // Reset navigation
    prevBtn.style.display = 'block';
    prevBtn.disabled = true;
    nextBtn.style.display = 'block';
    submitBtn.style.display = 'none';
    
    // Reset progress
    currentSection = 'physical';
    currentQuestionEl.textContent = 1;
    progressBar.style.width = '0%';
  });
});
