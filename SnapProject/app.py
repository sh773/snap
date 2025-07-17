from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

EXCEL_PATH = 'data/입결.xlsx'

def get_english_score(grade, score_str):
    score_list = [float(s.strip()) for s in score_str.split(',') if s.strip()]
    return score_list[grade - 1]

def calculate_student_score(row, inputs):
    국어 = inputs['국어']
    수학 = inputs['수학']
    탐구평균 = inputs['탐구평균']
    영어등급 = inputs['영어등급']

    영어점수 = get_english_score(영어등급, row['영어 등급별 환산점수'])

    # 반영비율 퍼센트 → 소수 변환
    국비 = row['반영비_국어'] / 100
    수비 = row['반영비_수학'] / 100
    탐비 = row['반영비_탐구'] / 100
    영비 = row['반영비_영어'] / 100

    score = (
        국어 * 국비 +
        수학 * 수비 +
        탐구평균 * 탐비 +
        영어점수 * 영비
    )
    return round(score, 2)

@app.route('/', methods=['GET', 'POST'])
def index():
    result_by_gun = {'가': [], '나': [], '다': []}
    my_input_info = None

    if request.method == 'POST':
        국어 = float(request.form['korean'])
        수학 = float(request.form['math'])
        탐구1 = float(request.form['science1'])
        탐구2 = float(request.form['science2'])
        영어등급 = int(request.form['english_grade'])

        탐구평균 = round((탐구1 + 탐구2) / 2, 2)

        inputs = {
            '국어': 국어,
            '수학': 수학,
            '탐구1': 탐구1,
            '탐구2': 탐구2,
            '탐구평균': 탐구평균,
            '영어등급': 영어등급
        }

        my_input_info = inputs

        df = pd.read_excel(EXCEL_PATH)

        for _, row in df.iterrows():
            my_score = calculate_student_score(row, inputs)

            try:
                cutoff = float(row["컷"])
            except (ValueError, TypeError):
                cutoff = 9999

            초과분 = round(my_score - cutoff, 2)
 
            if 초과분 <= 0:
                지원가능 = "불가능"
            elif 초과분 <= 2:
                지원가능 = "조금 가능"
            elif 초과분 <= 5:
                지원가능 = "가능"
            else:
                지원가능 = "매우 가능"

            record = {
                '대학_과': row['대학_과'],
                '컷': cutoff,
                '내환산점수': my_score,
                '지원가능': 지원가능,
                '초과': 초과분
            }

            군 = row['군']
            if 군 in result_by_gun:
                result_by_gun[군].append(record)

        for 군 in result_by_gun:
            result_by_gun[군].sort(key=lambda x: x['초과'], reverse=True)

    return render_template('index.html', result=result_by_gun, my_input=my_input_info)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
