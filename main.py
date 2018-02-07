import os
import csv
import cv2
import sys
from pathlib import Path
from collections import Counter

#what are the most extreme images of each emotion? (most of each)
#what are the images that had the largest gap between first and second?
#which images were the most evenly distributed emotions?
#which images had the biggest difference between positive and negative emotions?
#which is the least emotional image? has the highest % none?
#emotions by region of US?
#average number of emotion tags?

path_to_saved_images = '/Volumes/Seagate Backup Plus Drive/Hannah_Data/Datasets/AI_Grant/'
aggregated_results_csv = '../cf_report_1230552_aggregated.csv'
all_emotion_options = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust', 'none']

#keyword_index = 14
keyword_options = ['city', 'field', 'forest', 'mountain', 'ocean', 'lake', 'road']

font = cv2.FONT_HERSHEY_SIMPLEX
corner = (10,200)
fontScale = 1
fontColor = (255,255,255)
lineType = 2


def open_csv_results(csv_file):
    with open(csv_file, 'rb') as f:
        reader = csv.reader(f)
        results = list(reader)
    header = results[0]
    for i, item in enumerate(header):
        if header[i] == 'emotion_types':
            emotion_types_index = i 
        if header[i] == 'image_url':
            image_url_index = i
    return [results , emotion_types_index, image_url_index]

def show_image():
    if len(emotions) == 2:
        text_to_show = str(current_image_counter)+ '. '+ str(emotions[0])
        cv2.putText(img, text_to_show, corner, font, fontScale, fontColor, lineType)
        cv2.putText(img, str(emotions[1]), (corner[0], corner[1]+50), font, fontScale, fontColor, lineType)
    else:
        text_to_show = str(current_image_counter)+ '. '+ emotions
        cv2.putText(img, text_to_show, corner, font, fontScale, fontColor, lineType)
    cv2.imshow('image',img)
    cv2.waitKey(400)

# def process_url(url, keyword, emotions):
#     global current_image_name
#     global current_image_counter
#     image_filename = url.split('.com/')[1].split('/')[1]
#     if current_image_name == image_filename:
#         current_image_counter = current_image_counter + 1
#     else:
#         current_image_counter = 1
#     current_image_name = image_filename
#     #if there are more than 2 emotions, split up the text display
#     if len(emotions.split(',')) > 3:
#         separated_emotions = [', '.join(emotions.split(',')[0:2]), ', '.join(emotions.split(',')[2:])]
#         emotions = separated_emotions
#         print len(emotions)

#     path_to_img = path_to_saved_images + keyword + '/'+image_filename
#     img = cv2.imread(path_to_img,1)




def weight_by_proportion(entries):
    weighted_emotions = {}
    for entry in entries: 
        if '|' in entry:
            weight = 100.0/float(len(entry.split('|')))
            for emotion in entry.split('|'):
                if emotion in weighted_emotions:
                    weighted_emotions[emotion] = weighted_emotions[emotion] + weight
                else:
                    weighted_emotions[emotion] = weight
        else:
            weight = 100.0
            emotion = entry
            if emotion in weighted_emotions:
                weighted_emotions[emotion] = weighted_emotions[emotion] + weight
            else:
                weighted_emotions[emotion] = weight
    for key, value in weighted_emotions.iteritems():
        weighted_emotions[key] = float(weighted_emotions[key])/float(len(entries))
    return weighted_emotions

def weight_by_accumulation(entries):
    weight = 100.0
    weighted_emotions = {}
    for entry in entries: 
        if '|' in entry:
            for emotion in entry.split('|'):
                if emotion in weighted_emotions:
                    weighted_emotions[emotion] = weighted_emotions[emotion] + weight
                else:
                    weighted_emotions[emotion] = weight
        else:
            emotion = entry
            if emotion in weighted_emotions:
                weighted_emotions[emotion] = weighted_emotions[emotion] + weight
            else:
                weighted_emotions[emotion] = weight
    for e in weighted_emotions.keys():
        weighted_emotions[e] = float(weighted_emotions[e])/float(len(entries))
    return weighted_emotions

def parse_name_from_url(url):
    clean_url = url.split('.com/')[1].split('/')[1]
    return clean_url

def parse_results(emotion_types_index, image_url_index):
    counter = 0 
    all_weighted_emotions = {}
    for i, result  in enumerate(results):
        if i > 0:
            all_emotions = []
            entries = result[emotion_types_index].split('\n')
            weighted_emotions = weight_by_proportion(entries)
            for entry in entries:    
                if '|' in entry:
                    for emotion in entry.split('|'):
                        all_emotions.append(emotion.rstrip('\n'))
                else:
                    all_emotions.append(entry.rstrip('\n'))
            #weighted_emotions['url'] = result[image_url_index] 
            #result_name = parse_name_from_url(result[image_url_index])
            result_name = result[image_url_index]
            all_weighted_emotions[result_name] = weighted_emotions
    find_extremes(all_weighted_emotions)

def find_extremes(all_weighted_emotions):
    temporary_highest_values = {}
    for o in all_emotion_options:
        temporary_highest_values[o] = 0.0
    for key, value in all_weighted_emotions.iteritems():
        #print value
        for k in value.keys():
            # print k
            # print value[k]
            if temporary_highest_values[k] < float(value[k]):
                temporary_highest_values[k] = value[k]
    print temporary_highest_values

    # highest_values = {}
    # for o in all_emotion_options:
    #     highest_values[o] = []
    # for image_name, weighted_emotion in all_weighted_emotions.iteritems():
    #     for key in weighted_emotion.keys():
    #         if weighted_emotion[key] == 100.0:
    #             highest_values[key].append(weighted_emotion)

    # for item in highest_values:
    #     print item
    #     print len(highest_values[item])
    # print temporary_highest_values

def process_emotions(emotions):
    if '\n' in emotions:
        emotions = ', '.join(emotions.split('\n'))
    return emotions

results_and_indexes = open_csv_results(aggregated_results_csv)
results = results_and_indexes[0]
emotion_types_index = results_and_indexes[1]
image_url_index = results_and_indexes[2]

parse_results(emotion_types_index, image_url_index)




