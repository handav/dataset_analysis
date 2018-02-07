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
#top emotions per category
#top emotions that don't have any of the opposite (pos, neg) emotions associated

path_to_saved_images = '/Volumes/Seagate Backup Plus Drive/Hannah_Data/Datasets/AI_Grant/'
aggregated_results_csv = '../cf_report_1230552_aggregated.csv'
all_emotion_options = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust', 'none']
positive_emotions = ['joy', 'trust']
negative_emotions = ['anger', 'disgust', 'fear', 'sadness']
neutral_emotions = ['anticipation', 'surprise', 'none']

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

#same as proportion
def weight_by_percentage(entries):
    number_emotions = 0.0
    for entry in entries:
        if '|' in entry:
            number_emotions = number_emotions + len(entry.split('|'))
        else:
            number_emotions = number_emotions + 1.0
    print 'num', number_emotions
    weight = (100.0*float(len(entries)))/number_emotions
    print weight
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
    # for e in weighted_emotions.keys():
    #     weighted_emotions[e] = float(weighted_emotions[e])/float(len(entries))
    return weighted_emotions

#same as percentage
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
            weighted_emotions = weight_by_accumulation(entries)
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
    find_extreme_and_unique(all_weighted_emotions)

def find_extremes(all_weighted_emotions):
    temporary_highest_values = {}
    for o in all_emotion_options:
        temporary_highest_values[o] = 0.0
    for key, value in all_weighted_emotions.iteritems():
        for k in value.keys():
            if temporary_highest_values[k] < float(value[k]):
                temporary_highest_values[k] = value[k]

    highest_values = {}
    for o in all_emotion_options:
        highest_values[o] = []
    for image_name, weighted_emotion in all_weighted_emotions.iteritems():
        for key in weighted_emotion.keys():
            if weighted_emotion[key] == temporary_highest_values[key]:
                highest_values[key].append({image_name: weighted_emotion})

    for emotion in highest_values:
        print emotion
        print highest_values[emotion]

def find_extreme_and_unique(all_weighted_emotions):
    temporary_highest_values = {}
    for o in all_emotion_options:
        temporary_highest_values[o] = 0.0
    for key, value in all_weighted_emotions.iteritems():
        for k in value.keys():
            if temporary_highest_values[k] < float(value[k]):
                temporary_highest_values[k] = value[k]

    highest_values = {}
    for o in all_emotion_options:
        highest_values[o] = []

    for image_name, weighted_emotion in all_weighted_emotions.iteritems():
        is_unique = 0
        for key in weighted_emotion.keys():
            if weighted_emotion[key] == temporary_highest_values[key]:
                is_unique = is_unique + 1
                #highest_values[key].append({image_name: weighted_emotion})
        if is_unique == 1:
            for key in weighted_emotion.keys():
                if weighted_emotion[key] == temporary_highest_values[key]:
                    #is_unique = is_unique + 1
                    highest_values[key].append({image_name: weighted_emotion})


    for emotion in highest_values:
        print emotion
        print highest_values[emotion]
        print '\n'

def process_emotions(emotions):
    if '\n' in emotions:
        emotions = ', '.join(emotions.split('\n'))
    return emotions

results_and_indexes = open_csv_results(aggregated_results_csv)
results = results_and_indexes[0]
emotion_types_index = results_and_indexes[1]
image_url_index = results_and_indexes[2]

parse_results(emotion_types_index, image_url_index)




