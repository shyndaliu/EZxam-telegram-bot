import openai
import logging
import config

from datetime import timedelta, date, datetime
import re

openai.api_key = config.OPENAI_TOKEN


async def generate_text(prompt) -> dict:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1.3
        )
        return response['choices'][0]['message']['content'], response['usage']['total_tokens']
    except Exception as e:
        logging.error(e)


async def check_smth(prompt) -> dict:
    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "user", "content": prompt}
            ],
            temperature=1
        )
        return response['choices'][0]['message']['content'], response['usage']['total_tokens']
    except Exception as e:
        logging.error(e)


async def calendar_template(deadline_str):
    template = {}
    deadline = datetime.now()
    cur = datetime.now() + timedelta(hours=1)

    try:
        deadline = datetime.strptime(deadline_str.strip(), '%d.%m.%Y %H:%M')
    except ValueError:
        deadline = datetime.strptime(deadline_str.strip(), '%d.%m.%y %H:%M')

    while cur < deadline:
        date_str = cur.strftime("%d.%m")
        timespan_str = cur.strftime("%-I%p-")
        cur += timedelta(hours=1)
        timespan_str += cur.strftime("%-I%p")

        if not (date_str in template):
            template[date_str] = {}
        template[date_str][timespan_str] = False
    return template


async def cal_for_prompt(calendar):
    free_time = {}
    for date in calendar:
        date_data = calendar[date]
        timespan = []
        hours = list(date_data.keys())
        k = 0
        while k < len(hours) and (not date_data[hours[k]]):
            k+=1
        if k == len(hours):
            continue
        cur_timespan = re.findall(r"[0-9AMP]+", hours[k])
        for i in range(k+1, len(hours)):
            if date_data[hours[i]]:
                if len(cur_timespan) == 0:
                    cur_timespan = re.findall(r"[0-9AMP]+", hours[i])
                    continue
                split_hour = re.findall(r"[0-9AMP]+", hours[i])
                cur_timespan[1] = split_hour[1]
            else:
                if len(cur_timespan) == 0:
                    continue
                timespan.append("-".join(cur_timespan))
                cur_timespan.clear()
        if len(cur_timespan)!=0:
            timespan.append("-".join(cur_timespan))
        free_time[date] = timespan
    return free_time

async def count_time(calendar):
    answer = 0
    for date in calendar:
        for timespan in date:
            borders = re.findall(r"[0-9AMP]+", timespan)
            last = datetime.strptime(borders[1], '%-I%p')
            first = datetime.strptime(borders[0], '%-I%p')
            answer += int(last.timestamp() - first.timestamp()) // 60
    return answer
