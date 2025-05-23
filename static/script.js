document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('predictionForm');
    const resultContainer = document.getElementById('results');
    const simulationForm = document.getElementById('simulationForm');
    const loadingSpinner = document.getElementById('loadingSpinner');
    const errorMessage = document.getElementById('errorMessage');
    const downloadBtn = document.getElementById('downloadResult');
    let downloadData = null;


    // 🧮 Handle Prediction Form
    form.addEventListener('submit', function (e) {
        e.preventDefault();

        const formData = {
            annual_income: parseFloat(document.getElementById('annual_income').value),
            num_credit_card: parseInt(document.getElementById('num_credit_card').value),
            num_of_loan: parseInt(document.getElementById('num_of_loan').value),
            num_of_delayed_payment: parseInt(document.getElementById('num_of_delayed_payment').value),
            credit_utilization_ratio: parseFloat(document.getElementById('credit_utilization_ratio').value),
            credit_history_age: parseInt(document.getElementById('credit_history_age').value)
        };

        loadingSpinner.style.display = 'block';
        resultContainer.style.display = 'none';
        errorMessage.style.display = 'none';

        fetch('/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(formData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            displayResults(data);
        })
        .catch(error => showError("Error: " + error.message))
        .finally(() => {
            loadingSpinner.style.display = 'none';
        });
    });

    function displayResults(data) {
        const { score, rating, breakdown, message } = data;

        document.getElementById('creditScore').textContent = score;
        document.getElementById('predictionMessage').textContent = message;

        // Rating Badge
        const scoreBadgeEl = document.getElementById('scoreBadge');
        const achievementEl = document.getElementById('achievementBadge');

        switch (rating) {
            case "Excellent":
                scoreBadgeEl.textContent = "⭐ Excellent";
                achievementEl.textContent = "🏆 Top Performer!";
                break;
            case "Very Good":
                scoreBadgeEl.textContent = "🌟 Very Good";
                achievementEl.textContent = "";
                break;
            case "Good":
                scoreBadgeEl.textContent = "👍 Good";
                achievementEl.textContent = "";
                break;
            case "Fair":
                scoreBadgeEl.textContent = "⚠️ Fair";
                achievementEl.textContent = "";
                break;
            case "Poor":
                scoreBadgeEl.textContent = "🚫 Poor";
                achievementEl.textContent = "";
                break;
            default:
                scoreBadgeEl.textContent = "";
                achievementEl.textContent = "";
        }

        // Circle animation
        const scoreCircle = document.getElementById('scoreCircle');
        scoreCircle.style.animation = "bounce 0.6s";
        setTimeout(() => {
            scoreCircle.style.animation = "";
        }, 700);

        // Breakdown
        document.getElementById('paymentHistoryBar').style.width = `${(breakdown.payment_history / 150) * 100}%`;
        document.getElementById('paymentHistoryPoints').textContent = `${breakdown.payment_history} pts`;

        document.getElementById('creditUtilizationBar').style.width = `${(breakdown.credit_utilization / 150) * 100}%`;
        document.getElementById('creditUtilizationPoints').textContent = `${breakdown.credit_utilization} pts`;

        document.getElementById('creditAgeBar').style.width = `${(breakdown.credit_age / 150) * 100}%`;
        document.getElementById('creditAgePoints').textContent = `${breakdown.credit_age} pts`;

        document.getElementById('results').style.display = 'block';
        document.getElementById('simulationSection').style.display = 'block';

        showToast("Prediction successful!");
    }

    // 🧪 Simulation
    simulationForm.addEventListener('submit', function (e) {
        e.preventDefault();

        const improvements = {
            pay_bills_on_time: document.querySelector('input[name="pay_bills_on_time"]').checked,
            reduce_credit_utilization: document.querySelector('input[name="reduce_credit_utilization"]').checked,
            avoid_new_credit: document.querySelector('input[name="avoid_new_credit"]').checked
        };

        const currentScore = parseInt(document.getElementById('creditScore').textContent);

        fetch('/simulate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                current_score: currentScore,
                improvements: improvements
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                showError(data.error);
                return;
            }
            displaySimulationResults(data);
        })
        .catch(error => showError("Error: " + error.message));
    });

    function displaySimulationResults(data) {
        const currentScore = parseInt(document.getElementById('creditScore').textContent);

        document.getElementById('currentScoreValue').textContent = currentScore;
        document.getElementById('projectedScoreValue').textContent = data.projected_score;
        document.getElementById('simulationMessage').textContent = data.sim_message;

        const improvementBar = document.getElementById('improvementProgressBar');
        const improvementPoints = document.getElementById('improvementPoints');
        const totalImprovement = data.projected_score - currentScore;

        improvementBar.style.width = `${Math.min(100, (totalImprovement / 100) * 100)}%`;
        improvementPoints.textContent = `+${totalImprovement} points`;

        const improvementsList = document.getElementById('selectedImprovements');
        improvementsList.innerHTML = '';
        data.improvements_made.forEach(item => {
            const li = document.createElement('li');
            li.textContent = item;
            improvementsList.appendChild(li);
        });

        // Store for download
        downloadData = {
            inputs: {
                annual_income: document.getElementById('annual_income').value,
                num_credit_card: document.getElementById('num_credit_card').value,
                num_of_loan: document.getElementById('num_of_loan').value,
                delayed: document.getElementById('num_of_delayed_payment').value,
                utilization: document.getElementById('credit_utilization_ratio').value,
                age: document.getElementById('credit_history_age').value
            },
            current_score: data.current_score,
            projected_score: data.projected_score,
            improvements: data.improvements_made,
            message: data.sim_message
        };

        document.getElementById('simulationResults').style.display = 'block';
        downloadBtn.style.display = 'inline-block';

        showToast("Simulation complete!");
    }

    // 📥 Download Full Results
    downloadBtn.addEventListener('click', function () {
        if (!downloadData) {
            alert("Please run a simulation first.");
            return;
        }

        const input = downloadData.inputs;
        const improvementList = downloadData.improvements.map(i => `- ${i}`).join('\n');
        const scoreDiff = downloadData.projected_score - downloadData.current_score;

        const fileContent = `
CREDIT SCORE REPORT

📝 USER INPUTS:
- Annual Income: $${input.annual_income}
- Credit Cards: ${input.num_credit_card}
- Loans: ${input.num_of_loan}
- Delayed Payments: ${input.delayed}
- Credit Utilization: ${input.utilization}%
- Credit History Age: ${input.age} months

📊 PREDICTED SCORE: ${downloadData.current_score}
📈 PROJECTED SCORE: ${downloadData.projected_score}
⬆️ TOTAL GAIN: +${scoreDiff} points

✅ SIMULATION CHANGES:
${improvementList}

💬 ADVICE:
${downloadData.message}
        `.trim();

        const blob = new Blob([fileContent], { type: 'text/plain' });
        const a = document.createElement('a');
        a.href = URL.createObjectURL(blob);
        a.download = 'credit_score_full_report.txt';
        a.click();
    });

    // 🔔 Toast Notification
    function showToast(message) {
        const toast = document.getElementById('toast');
        toast.textContent = message;
        toast.style.display = 'block';
        setTimeout(() => {
            toast.classList.add('show');
        }, 100);
        setTimeout(() => {
            toast.classList.remove('show');
            toast.style.display = 'none';
        }, 3000);
    }

    // ❗ Show error
    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.style.display = 'block';
        setTimeout(() => {
            errorMessage.style.display = 'none';
        }, 5000);
    }
});
