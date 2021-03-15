from math import radians, sin, cos


class CreatePara:
    def __init__(self, phrase, filename):
        self.phrase = phrase
        self.filename = filename
        self.mult = 0.55
        self.mid_x = 400
        self.mid_y = 400
        self.file_text = '''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
        <!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 20010904//EN"
        "http://www.w3.org/TR/2001/REC-SVG-20010904/DTD/svg10.dtd">
        
        <svg xmlns="http://www.w3.org/2000/svg"
        width="6in" height="6in"
        viewBox="0 0 800 800">
        '''
        self.oa_out_radius = 300
        self.oa_in_radius = 270

        self.ia_out_radius = 255
        self.ia_zigzag_1 = 205
        self.ia_zigzag_2 = 190
        self.ia_zigzag_3 = 120
        self.ia_zigzag_4 = 110
        self.ia_in_radius = 30

        self.inner_dict = {}
        self.inner_shape = None
        self.diagonal_dict = {}
        peaks = [i / 10 for i in range(0, 3600, 90)]
        troughs = [i / 10 for i in range(45, 3600, 90)]
        for p in peaks:
            self.diagonal_dict[p]['outer'] = 205
            self.diagonal_dict[p]['inner'] = 120
        for t in troughs:
            self.diagonal_dict[t]['outer'] = 190
            self.diagonal_dict[t]['inner'] = 110

        self.curr_deg = 0
        self.first_pass()
        self.test_arc()
        self.save_file()

    def get_xy(self, rad, deg):
        opp = rad * sin(radians(deg))
        adj = rad * cos(radians(deg))
        x1 = self.mid_x + opp
        y1 = self.mid_y - adj

        return x1, y1

    def get_points(self, rad, deg, deg_diff, loc):
        x1, y1 = get_xy(rad, deg)
        vector_opp = (self.mult * (deg_diff / 90) * rad * sin(radians(deg)))
        vector_adj = (self.mult * (deg_diff / 90) * rad * cos(radians(deg)))
        if loc == 'arc':
            x2 = x1 + vector_adj
            y2 = y1 + vector_opp
        elif loc == 'corner':
            x2 = x1 - vector_adj
            y2 = y1 - vector_opp

        return x1, y1, x2, y2

    def get_binary(self, letter):
        try:
            num_code = int(letter)
        except ValueError:
            num_code = ord(letter.lower()) - 96
        bin_col = 64
        arc_list = []
        while bin_col >= 1:
            if num_code >= bin_col:
                arc_list.append(True)
                num_code -= bin_col
            else:
                arc_list.append(False)
            bin_col /= 2

        return arc_list

    def increment_deg(self, inc_deg, rd_ct=1):
        for i in range(rd_ct):
            inc_deg += 4.5
            if inc_deg == 360:
                inc_deg = 0

        return inc_deg

    def outer_ring(self, out_rad, st_deg, end_deg, in_rad):
        st_x, st_y, sv_x, sv_y = self.get_points(out_rad, st_deg, end_deg - st_deg, 'arc')
        c1_x, c1_y, c1v_x, c1v_y = self.get_points(out_rad, end_deg, end_deg - st_deg, 'corner')
        c2_x, c2_y, c2v_x, c2v_y = self.get_points(in_rad, end_deg, end_deg - st_deg, 'corner')
        end_x, end_y, ev_x, ev_y = self.get_points(in_rad, st_deg, end_deg - st_deg, 'arc')

        arc = '''<path id="final"
                fill="none" stroke="black" stroke-width="3"
                d="'''
        arc += f'   M {st_x},{st_y}\n'
        arc += f'   C {sv_x},{sv_y} ' \
               f'{c1v_x},{c1v_y} ' \
               f'{c1_x},{c1_y}\n'
        arc += f'   C {c2_x},{c2_y} ' \
               f'{c1_x},{c1_y} ' \
               f'{c2_x},{c2_y}\n'
        arc += f'   C {c2v_x},{c2v_y} ' \
               f'{ev_x},{ev_y} ' \
               f'{end_x},{end_y}\n'
        arc += f'   Z\n'
        arc += '"'
        arc += '/>\n'

        self.file_text += arc

    def outer_arc(self, st_deg, end_deg):
        st_x, st_y, sv_x, sv_y = self.get_points(self.ia_out_radius, st_deg, end_deg - st_deg, 'arc')
        c_x, c_y, cv_x, cv_y = self.get_points(self.ia_out_radius, end_deg, end_deg - st_deg, 'corner')

        if self.inner_shape is None:
            self.inner_shape = '''<path id="final"
            fill="none" stroke="black" stroke-width="3"
            d="'''
            self.inner_shape += f'   M {st_x},{st_y}\n'
        self.inner_shape += f'   C {sv_x},{sv_y} ' \
                            f'{cv_x},{cv_y} ' \
                            f'{c_x},{c_y}\n'

        return c_x, c_y

    def straight_line(self, ring, deg, c1_x, c1_y):
        if ring == 'center':
            rad = self.ia_in_radius
        else:
            rad = self.diagonal_dict[deg][ring]

        c2_x, c2_y = self.get_xy(rad, deg)
        self.inner_shape += f'   C {c2_x},{c2_y} ' \
                            f'{c1_x},{c1_y} ' \
                            f'{c2_x},{c2_y}\n'

        return c2_x, c2_y

    def inner_arc(self, in_rad, st_deg, end_deg):
        _, _, c2v_x, c2v_y = self.get_points(self.ia_in_radius, st_deg, st_deg - end_deg, 'corner')
        end_x, end_y, ev_x, ev_y = self.get_points(in_rad, st_deg, st_deg - end_deg, 'arc')

        self.inner_shape += f'   C {c2v_x},{c2v_y} ' \
                            f'{ev_x},{ev_y} ' \
                            f'{end_x},{end_y}\n'

        return c_x, c_y

    def close_shape(self):
        self.inner_shape += f'   Z\n'
        self.inner_shape += '"'
        self.inner_shape += '/>\n'

        self.file_text += self.inner_shape
        self.inner_shape = None

    def first_pass(self):
        inner_dict = {}
        for rd, word in enumerate(words):
            word_start_deg = self.curr_deg
            if rd < 3:
                rd_str = f'level_{rd + 1}'
                inner_dict[rd_str] = {}
                for l in word:
                    bin_list = self.get_binary(l)
                    for inner_slice in bin_list:
                        inner_dict[rd_str][self.curr_deg] = [inner_slice, False]
                        self.curr_deg = self.increment_deg(self.curr_deg)
                    for i in range(3):
                        inner_dict[rd_str][self.curr_deg] = [False, False]
                        self.curr_deg = self.increment_deg(self.curr_deg)
                print(f'word finished at deg: {self.curr_deg}, needs to go back round to {word_start_deg}')
                deg = self.curr_deg
                if word_start_deg < deg:
                    while (deg <= 360) and (deg > 0):
                        if deg not in inner_dict[rd_str].keys():
                            inner_dict[rd_str][deg] = [True, False]
                        else:
                            print(f'first DUPE - {deg}')
                        deg = self.increment_deg(deg)
                if (word_start_deg) < 0:
                    stop_deg = 360 + (word_start_deg)
                else:
                    stop_deg = word_start_deg
                print(stop_deg)
                while deg < stop_deg:
                    if deg not in inner_dict[rd_str].keys():
                        inner_dict[rd_str][deg] = [True, False]
                    else:
                        print(f'second DUPE - {deg}')
                    deg = self.increment_deg(deg)
                '''for i in range(3):
                    if deg not in inner_dict[rd_str].keys():
                        inner_dict[rd_str][deg] = [False, False]
                    else:
                        print(f'third DUPE - {deg}')
                    deg = self.increment_deg(deg)'''
            else:
                for l in word:
                    bin_list = self.get_binary(l)
                    arc_start_deg = None
                    for arcslice in bin_list:
                        if arc_start_deg is None:
                            if arcslice:
                                arc_start_deg = self.curr_deg
                        else:
                            if not arcslice:
                                self.outer_ring(self.oa_out_radius,
                                              arc_start_deg,
                                              self.curr_deg,
                                              self.oa_in_radius)
                                arc_start_deg = None
                        self.curr_deg = self.increment_deg(self.curr_deg)
                    if arc_start_deg is not None:
                        self.outer_ring(self.oa_out_radius,
                                      arc_start_deg,
                                      self.curr_deg,
                                      self.oa_in_radius)
                    self.curr_deg = self.increment_deg(self.curr_deg, 3)
        self.inner_dict = inner_dict

    def test_arc(self):
        test_deg = 0
        test_arc_start_deg = None
        while True:
            if self.inner_dict['level_3'][test_deg][0]:
                if test_arc_start_deg is None:
                    test_arc_start_deg = test_deg
            else:
                if test_arc_start_deg is not None:
                    self.outer_ring(self.ia_out_radius,
                                  test_arc_start_deg,
                                  test_deg,
                                  self.ia_in_radius)
                    break
            test_deg += 4.5

    def save_file(self):
        self.file_text += '</svg>'

        with open(self.filename + ".svg", "w") as sv:
            sv.write(self.file_text)


filename = 'para_test'
words = ['dare', 'mighty', 'things', ['34', '11', '58', 'n', '118', '10', '31', 'w']]

if __name__ == '__main__':
    CreatePara(words, filename)
