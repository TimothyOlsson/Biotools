import numpy as np
import time
import sys
import multiprocessing


class Needleman_Wunsch():
  
  def __init__(self, match=1, mismatch=-1, gap=-1):
    self.match = match
    self.mismatch = mismatch
    self.gap = gap
    self.point_list = ['D','V','H']

  def check_match(self,n1,n2):
    if n1==n2:
      return self.match
    else:
      return self.mismatch

  def check_pointer(self,list_of_values):
    indices = [i for i, x in enumerate(list_of_values) if x == max(list_of_values)]
    pointer=''
    for i in indices:
      pointer += self.point_list[i]
    return pointer

  def calc_score(self, seq1, seq2):
    if len(seq1) != len(seq2):
      print('Seqs are not same lengths. Align first')
      return
    score = 0
    amount_of_matches = 0
    amount_of_mismatches = 0
    amount_of_gaps = 0
    for i in range(0,len(seq1)):
      if seq1[i] == '-' or seq2[i] == '-':
        score += self.gap
        amount_of_gaps += 1          
      elif seq1[i] != seq2[i]:
        score += self.mismatch
        amount_of_mismatches +=1
      elif seq1[i] == seq2[i]:
        score += self.match
        amount_of_matches += 1
      else:
        print('Something went wrong when checking score')
        return
    match_percentage = amount_of_matches/len(seq1)
    return score, match_percentage, amount_of_matches, amount_of_mismatches, amount_of_gaps

  def alignment_indication(self, seq1, seq2):
    alignment_indication = []
    for i in range(0,len(seq1)):
      if (seq1[i] == '-') or (seq2[i] == '-'):
        alignment_indication.append(' ')
      elif seq1[i] != seq2[i]:
        alignment_indication.append(':')
      elif seq1[i] == seq2[i]:
        alignment_indication.append('|')
      else:
        print('Something went wrong when checking score')
        return
    return ''.join(alignment_indication)

  def traceback(self, seq1, seq2, score_matrix, pointer_matrix):
      #Lists are faster than strings
      aligned_seq1 = []
      aligned_seq2 = []
      n = len(seq1)
      m = len(seq2)
      x,y = [n,m]

      done = False
      while done!=True:
        if pointer_matrix[x][y] == 'D':
          aligned_seq1.append(seq1[x-1])
          aligned_seq2.append(seq2[y-1])
          x -= 1
          y -= 1
        elif pointer_matrix[x][y] == 'H':
          aligned_seq1.append('-')
          aligned_seq2.append(seq2[y-1])
          y -= 1
        elif pointer_matrix[x][y] == 'V':
          aligned_seq1.append(seq1[x-1])
          aligned_seq2.append('-')
          x -= 1
        elif pointer_matrix[x][y] == 'E':
          done=True
        else:
          quit #should never get here

      return ''.join(reversed(aligned_seq1)), ''.join(reversed(aligned_seq2))

  def calc_matrix(self,seq1,seq2):
    """
    a[0][1] = a[x1][y2]
      y1 y2 y3
    x1
    x2
    x3

      s  e  q  2
    s
    e
    q
    1
    """

    n = len(seq1) + 1
    m = len(seq2) + 1
    score_matrix = np.zeros((n,m), dtype=int) #Stores ints
    pointer_matrix = np.zeros((n,m), dtype=str) #Stores strings
    
    for i in range(1,n):
      score_matrix[i][0] = i*self.gap
      pointer_matrix[i][0] = 'V'
    for i in range(1,m):
      score_matrix[0][i] = i*self.gap
      pointer_matrix[0][i] = 'H'
      
    pointer_matrix[0][0] = 'E'

    for i in range(1,n):
      for j in range(1,m):
        diagonal = score_matrix[i-1][j-1] + self.check_match(seq1[i-1], seq2[j-1])
        vertical = score_matrix[i-1][j] + self.gap
        horisontal = score_matrix[i][j-1] + self.gap
        score_matrix[i][j] = max(diagonal, vertical, horisontal)
        pointer_matrix[i][j] = self.check_pointer([diagonal, vertical, horisontal])
    
    return score_matrix,pointer_matrix

  def run(self, seq1, seq2, queue=multiprocessing.Queue()):

    score_matrix, pointer_matrix = self.calc_matrix(seq1,seq2)
    aligned_seq1, aligned_seq2 = self.traceback(seq1,seq2,score_matrix,pointer_matrix)
    score, match_percentage, amount_of_matches, amount_of_mismatches, amount_of_gaps = self.calc_score(aligned_seq1, aligned_seq2)
    alignment_indication = self.alignment_indication(aligned_seq1, aligned_seq2)

    list_of_all_things = [#[x.tolist() for x in score_matrix], #Not needed
                          #[x.tolist() for x in pointer_matrix], #Not needed
                          aligned_seq1,
                          alignment_indication,
                          aligned_seq2,
                          score,
                          match_percentage,
                          amount_of_matches,
                          amount_of_mismatches,
                          amount_of_gaps]

    dict_of_all_things = {#'score_matrix':#[x.tolist() for x in score_matrix], #Not needed
                          #'pointer_': [x.tolist() for x in pointer_matrix], #Not needed
                          'aligned_seq1': aligned_seq1,
                          'alignment_indication': alignment_indication,
                          'aligned_seq2': aligned_seq2,
                          'score': score,
                          'match_percentage': match_percentage,
                          'amount_of_matches': amount_of_matches,
                          'amount_of_mismatches': amount_of_mismatches,
                          'amount_of_gaps': amount_of_gaps}

    time.sleep(5)
    queue.put(dict_of_all_things)
    
    for i in list_of_all_things:
      print(i)
    
    return list_of_all_things
    
    
if __name__=='__main__':
  """
  p1 = Process(target=func1)
  p1.start()
  p2 = Process(target=func2)
  p2.start()
  """













  
