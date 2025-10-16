

import csv
import random
import json 

''' Natural language with multiple mitigation steps '''

state_classification = {
    "driver_actions": {
        "reach_side": "distraction",
        "reach_backseat": "high_distraction",
        "radio": "distraction",
        "hair_and_makeup": "high_distraction",
        "drinking": "distraction",
        "texting_right": "high_distraction",
        "texting_left": "high_distraction",
        "phonecall_right": "distraction",
        "phonecall_left": "distraction",  
    },
    "hands_using_wheel": {
        "none": "high_distraction"
    },
    "talking": {
        "talking": "distraction",
    },
    "gaze_on_road": {
        "not_looking_road": "high_distraction"
    },
    "eyes_state": {
        "closing": "drowsiness",
        "close": "drowsiness"
    },
    "yawning": {
        "Yawning without hand": "drowsiness",
        "Yawning with hand": "drowsiness",
        "Yawning": "drowsiness",
    }
}


def classify_behavior(csv_filename, output_file):
    scenarios_list = []
    with open(csv_filename, "r", encoding="utf-8", newline="") as f_in, \
         open(output_file, "w", encoding="utf-8", newline="") as f_out:

        reader = csv.DictReader(f_in)
        fieldnames = reader.fieldnames + ["classification"]
        writer = csv.DictWriter(f_out, fieldnames=fieldnames)
        writer.writeheader()

        for row in reader:
            classifications = set()  # use a set to avoid duplicates

            # Check each column in the row against your classification mappings
            for col, mapping in state_classification.items():
                if col in row and row[col] in mapping:
                    classifications.add(mapping[row[col]])

            # Handle case if no condition matched
            if not classifications:
                classifications.add("safe")

            # Convert the set to a comma-separated string for CSV output
            row["classification"] = ",".join(sorted(classifications))
            scenarios_list.append(row)
            writer.writerow(row)
        print("saved as csv classified", output_file)
    return scenarios_list

def detect_drowsiness(scenario):
     # Detect drowsiness second 
    response = random.choice(["Drowsiness detected. Please open the window for air.", "Play some upbeat music, you seem drowsy."])
    return response

def detect_high_distraction(scenario):
     # means not looking at road
                                                        # or make up or texting, backseat 
    # Focus on risky behavior 
    if scenario["hands_using_wheel"] == "none":
        response = "Keep one hand at 8, one at 4."
    
    if scenario["gaze_on_road"] == "not_looking_road":
        response = "Please look ahead, every second matters."
    
    if scenario["driver_actions"] == "reach_backseat":
        response = "Please pull aside to reach to backseat."
    
    if scenario["driver_actions"] == "texting_left" or "texting_right":
        response = random.choice(["Reminder to set your phone to Do Not Disturb.","Please use voice assistants to send messages."])
    if scenario["driver_actions"] == "hair_and_makeup":
        response = random.choice(["Please wait until end of the trip for touch ups.", "Pull aside to get ready."])
    response = "Distraction detected."
    return response

def detect_high_speed(scenario):
    if scenario["traffic_density"] == "high":
        response = random.choice(["Be careful driving off the road, traffic is dense.", "Stay in your lane during traffic congestion."])
    
    elif scenario["road_type"] == "highway" and scenario["eyes_state"] in ["close", "closing"]:
        response = "Reminder, a blink can cost you a long stretch of awareness."

    else:
        response = "Car speed is dangerously over speed limit."

    return response

def detect_speed(scenario):
    response = "Please stay within speed limit."
    return response

def detect_bad_weather(scenario):
    if scenario["weather"] == "fog":
        response = "Turn on fog lights."

    if scenario["weather"] in ["snow", "rain"]:
        response = "Keep a 6 to 8 seconds following distance due to bad weather."

    return response

def detect_distraction(scenario):
    
    if scenario["driver_actions"] == "phonecall_left" or "phonecall_right":
        response = "Please use the car’s built-in audio."
   
    if scenario["talking"] == "talking":
        response = random.choice(["Reminder to avoid charged conversations.", "Please keep conversations light hearted."])
    
    if scenario["driver_actions"] == "drinking":
        response = "Please keep sips small."
    return response

def detect_congestion(scenario):
    if scenario["traffic_density"] == "high" and scenario["road_type"] == "highway":
        response = "If you can't see car's mirror, they can't see you."
    if scenario["traffic_density"] == "high":
        response = "Watch front wheels of cars merging."
    if scenario["traffic_density"] == "medium" and scenario["time_of_day"] == "night" and scenario["road_type"] == ["rural", "highway"]:
        #if scenario["time_of_day"] == "night" and scenario["road_type"] in ["highway", "rural"]:
        response = "Make sure you are able to stop whithin range of your headlights."    
    response = "Please look 10 to 15 seconds ahead."
    return response

def clean_value(input_dict, default="unknown"):
    #print("input.keys()", input_dict.keys())
    for key in input_dict.keys():
        #print("input_dict[key]", input_dict[key])
        #print("key", key)
        val = input_dict[key]
        if isinstance(val, str) and val.strip().lower() == "na":
            input_dict[key] = "unknown_value"
            #print(f"Replaced '{key}' with:", input_dict[key])
        else:
            #print("pass")
            pass
    return input_dict

def generate_advice(scenarios_list):
    ''' Advice based on priority risk. 
        De-escalate risk for each scenario. '''
    
    results = []
    general_input = "The driver is {driver_actions}, {gaze_on_road}, and using {hands_using_wheel} hand(s) on the wheel. Driver is {talking} and/or {yawning} and his eyes {eyes_state}.Weather is {weather}, traffic is {traffic_density}, and the car is {car_speed} speed limit on a {road_type} road. Behavior classification detected: {classification}."
    
    for scenario in scenarios_list:
        #print(scenario)
        input_dict = {
            "driver_actions": scenario["driver_actions"],
            "gaze_on_road": scenario["gaze_on_road"],
            "hands_using_wheel": scenario["hands_using_wheel"],
            "talking": scenario["talking"],
            "eyes_state": scenario["eyes_state"],
            "weather": scenario["weather"],
            "yawning": scenario["yawning"],
            "traffic_density": scenario["traffic_density"],
            "car_speed": scenario["car_speed"],
            "road_type": scenario["road_type"],
            "classification": scenario["classification"]
        }

        #Remove NA from dictionary to avoid training model issues
        input_dict = clean_value(input_dict, "unknown_value")
        input_text  = general_input.format(**input_dict)
        #break
        #print("input_text", input_text)

        # Check for combined high-risk scenarios
        advice = []

        if scenario["car_speed"] == "severe_over" and scenario["classification"] == "distraction,drowsiness,high_distraction":
            advice1 = detect_high_speed(scenario)
            advice2 = detect_high_distraction(scenario)
            advice.extend([advice1, advice2])

        elif scenario["car_speed"] == "severe_over" and scenario["classification"] == "drowsiness,high_distraction":
            advice2 = "Distraction and drowsiness detected."
            advice1 = detect_high_speed(scenario)
            advice.extend([advice1, advice2])

        elif scenario["car_speed"] == "severe_over" and  scenario["classification"] == "distraction,high_distraction":
            advice2 = detect_high_distraction(scenario)
            advice1 = detect_high_speed(scenario)
            advice.extend([advice1, advice2])

        elif scenario["car_speed"] == "severe_over" and scenario["classification"] == "distraction,drowsiness":
            advice1 = detect_high_speed(scenario)
            advice2 = detect_drowsiness(scenario)
            advice.extend([advice1, advice2])

        elif scenario["car_speed"] == "severe_over" and scenario["classification"] == "high_distraction":
            #advice.append("Stay focused and slow down — distractions at high speed are deadly.")
            advice2 = detect_high_distraction(scenario)
            advice1 = detect_high_speed(scenario)
            advice.extend([advice1, advice2])

        elif scenario["car_speed"] == "severe_over" and scenario["classification"] == "drowsiness":
            #advice.append("Slow down and take a rest if feeling drowsy.")
            advice1 = detect_high_speed(scenario)
            advice2 = detect_drowsiness(scenario)
            advice.extend([advice1, advice2])

        elif scenario["classification"] == "distraction,drowsiness,high_distraction":
            advice1 = detect_high_distraction(scenario)
            advice2 = detect_drowsiness(scenario)
            advice.extend([advice1, advice2])

        elif scenario["classification"] == "drowsiness,high_distraction":
            advice1 = detect_high_distraction(scenario)
            advice2 = detect_drowsiness(scenario)
            advice.extend([advice1, advice2])
        
        elif scenario["classification"] == "distraction,high_distraction":
            advice1 = detect_high_distraction(scenario)
            advice2 = detect_distraction(scenario)
            advice.extend([advice1, advice2])
        
        elif scenario["classification"] == "distraction,drowsiness":
            advice1 = detect_drowsiness(scenario)
            advice2 = detect_distraction(scenario)
            advice.extend([advice1, advice2])
        
        elif scenario["weather"] in ["rain", "snow", "fog"] and scenario["car_speed"] == "over":
            #advice.append("Reduce speed and drive carefully in adverse weather.")
            advice1 = detect_speed(scenario)
            advice2 = detect_bad_weather(scenario)
            advice.extend([advice1, advice2])

        elif scenario["classification"] == "high_distraction" and scenario["traffic_density"] in ["high", "medium"]:
            #advice.append("Focus on the road and keep a safe distance in traffic.")
            advice1 = detect_high_distraction(scenario)
            advice2 = detect_congestion(scenario)
            advice.extend([advice1, advice2])

        elif scenario["classification"] == "drowsiness" and scenario["traffic_density"] in ["high", "medium"]:
            #advice.append("Keep your distance, slow down, or pull over if tired.")
            advice1 = detect_drowsiness(scenario)
            advice2 = detect_congestion(scenario)
            advice.extend([advice1, advice2])

        else: # Handle individual risks here
            
            # over speeding 
            if scenario["car_speed"] == "severe_over":
                advice = [detect_high_speed(scenario)]
            
            elif scenario["classification"] == "high_distraction":
                advice = [detect_high_distraction(scenario)]

           # drowsiness
            elif scenario["classification"] == "drowsiness":
                advice = [detect_drowsiness(scenario)]

            # disctraction
            elif scenario["classification"] == "distraction":
                advice = [detect_distraction(scenario)]

            # speed
            elif scenario["car_speed"] in ["over", "under"]:
                advice = [detect_speed(scenario)]

            # traffic
            elif scenario["traffic_density"] in ["high", "medium"]:
                advice = [detect_congestion(scenario)]

            elif scenario["traffic_density"] == "low" and scenario["time_of_day"] == "night" and scenario["road_type"] == "rural":
                advice = ["Make sure you are able to stop whithin range of your headlights."] 
            
            # weather
            elif scenario["weather"] in ["rain", "snow", "fog"]:
                advice = [detect_bad_weather(scenario)]

            #road type
            elif scenario["road_type"] == "highway":
                advice = ["Avoid fast lane unless actively passing."]

            elif scenario["road_type"] == "urban":
                advice = ["Check mirrors every 5 to 8 seconds."]

            elif scenario["road_type"] == "rural":
                advice = ["Keep your eyes moving every 2 or 3 seconds."]

            elif scenario["driver_actions"] == "standstill_or_waiting":
                advice = ["Keep your wheels straight."]
                
            elif scenario["driver_actions"] ==  "safe_drive" and scenario["car_speed"] == "none":
                advice = ["Keep your eyes moving every 2 or 3 seconds."]
            else:
                advice = ["Keep your eyes moving every 2 or 3 seconds."]

        # Limit advice to maximum 2 per scenario
        advice = advice[:2]
        advice_text = " ".join(advice)

        results.append({"input": input_text, "advice": advice_text})
    return results

def save_as_jsonl(instruction, data, output_filepath):
    with open(output_filepath, "w", encoding="utf-8") as f_out:
        for record in data:
            json_record = {
                "instruction": instruction,
                "input": record["input"],
                "output": record["advice"]
            }
            f_out.write(json.dumps(json_record) + "\n")
    print("saved as json l", output_filepath)

def save_as_csv(data, output_filepath):
    # does not include instruction
    with open(output_filepath, "w", newline='', encoding="utf-8") as f_out:
        writer = csv.DictWriter(f_out, fieldnames=["input", "advice"])
        writer.writeheader()
        for record in data:
            writer.writerow(record)
    print("saved as csv", output_filepath)

def main():
    instruction = "Give driving advice based on the situation"

    # Training Data Classified and Unique Filenames
    csv_training_filename = "training_scenarios_combined_unique.csv"
    csv_training_classified = "training_scenarios_combined_unique_classified.csv"
    # Training Advice Filenames 
    training_advice_csv_filename = "training_advice.csv"
    training_advice_jsonl_filename = "training_advice.jsonl"

     # Classify and generate training advice, then save after shuffling
    scenarios_training_classified  = classify_behavior(csv_training_filename, csv_training_classified)
    training_results = generate_advice(scenarios_training_classified)
    random.shuffle(training_results)
    save_as_csv(training_results, training_advice_csv_filename)
    save_as_jsonl(instruction, training_results, training_advice_jsonl_filename)

   
    # Testing Data Classified and Unique Filenames
    csv_testing_filename = "testing_scenarios_combined_unique.csv"
    csv_testing_classified = "testing_scenarios_combined_unique_classified.csv"
    # Testing Advice Filenames
    testing_advice_csv_filename = "testing_advice.csv"
    testing_advice_jsonl_filename = "testing_advice.jsonl"

    # Classify and generate testing advice, then save after shuffling 
    scenarios_testing_classified = classify_behavior(csv_testing_filename, csv_testing_classified)
    testing_results = generate_advice(scenarios_testing_classified)
    random.shuffle(testing_results)
    save_as_csv(testing_results, testing_advice_csv_filename)
    save_as_jsonl(instruction, testing_results, testing_advice_jsonl_filename)

    # check unique
    # move 80 percent of testing data to training

    print(f"New training set size: {len(training_results)}")
    print(f"New testing set size: {len(testing_results)}")
    #New training set size: 10168
    #New testing set size: 9923

if __name__ == "__main__":
    main()


