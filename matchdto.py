from datetime import datetime, timedelta
import calendar
import copy


GOAL_ZH_HK = u"\u5E73\u624B,\u5E73/\u534A,\u534A\u7403,\u534A/\u4E00,\u4E00\u7403,\u4E00/\u7403\u534A,\u7403\u534A," \
          u"\u7403\u534A/\u4E24,\u4E24\u7403,\u4E24/\u4E24\u7403\u534A,\u4E24\u7403\u534A,\u4E24\u7403\u534A/\u4E09," \
          u"\u4E09\u7403,\u4E09/\u4E09\u7403\u534A,\u4E09\u7403\u534A,\u4E09\u7403\u534A/\u56DB\u7403,\u56DB\u7403," \
          u"\u56DB/\u56DB\u7403\u534A,\u56DB\u7403\u534A,\u56DB\u7403\u534A/\u4E94,\u4E94\u7403," \
          u"\u4E94/\u4E94\u7403\u534A,\u4E94\u7403\u534A,\u4E94\u7403\u534A/\u516D,\u516D\u7403," \
          u"\u516D/\u516D\u7403\u534A,\u516D\u7403\u534A,\u516D\u7403\u534A/\u4E03,\u4E03\u7403," \
          u"\u4E03/\u4E03\u7403\u534A,\u4E03\u7403\u534A,\u4E03\u7403\u534A/\u516B,\u516B\u7403," \
          u"\u516B/\u516B\u7403\u534A,\u516B\u7403\u534A,\u516B\u7403\u534A/\u4E5D,\u4E5D\u7403," \
          u"\u4E5D/\u4E5D\u7403\u534A,\u4E5D\u7403\u534A,\u4E5D\u7403\u534A/\u5341,\u5341\u7403 "


class MatchInfo:
    def __init__(self, json_object):
        self.id = json_object[0]
        self.lg_co = json_object[1]
        self.lg_sc = json_object[2]
        self.lg_tc = json_object[3]
        self.lg_en = json_object[4]
        self.ht_sc = json_object[5]
        self.ht_tc = json_object[6]
        self.ht_en = json_object[7]
        self.at_sc = json_object[8]
        self.at_tc = json_object[9]
        self.at_en = json_object[10]
        self.sch_start_time = json_object[11]
        self.status = int(json_object[13])
        self.ht_ft_score = json_object[14]
        self.at_ft_score = json_object[15]
        self.ht_ht_score = json_object[16]
        self.at_ht_score = json_object[17]
        self.ht_red_card = json_object[18]
        self.at_red_card = json_object[19]
        self.ht_yellow_card = json_object[20]
        self.at_yellow_card = json_object[21]
        self.lg_ht_rank = json_object[22]
        self.lg_at_rank = json_object[23]
        self.lg_url = json_object[30]
        date_array = json_object[12].split(",")
        date_string = ""
        for idx in range(len(date_array)):
            date_string += "" if (date_string == "") else ","
            date_string += date_array[idx] #if (idx != 1) else str(int(date_array[idx])+1)
        self.actual_date = datetime.strptime(date_string, '%Y,%m,%d,%H,%M,%S')
        days_in_month = calendar.monthrange(self.actual_date.year, self.actual_date.month)[1]
        self.actual_date += timedelta(days=days_in_month)
        self.actual_date -= timedelta(hours=8)

        self.raw_odds = None

    def set_raw_odds(self, raw_odds):
        self.raw_odds = raw_odds

    @property
    def actual_date_timestamp(self):
        return self.actual_date.timestamp() * 1000

    @property
    def status_text(self):
        __delta__ = self.actual_date - datetime.now()
        __minute_diff__ = abs(int(__delta__.total_seconds() / 60))
        if self.status == -1:
            return u'\u5B8C'
        elif self.status == 1:
            return str(__minute_diff__)
        elif self.status == 2:
            return u'\u534A'
        elif self.status == 3:
            return str(__minute_diff__ + 45)
        elif self.status == 4:
            return u'\u52A0'
        return ''

    @property
    def odds(self):
        return self.raw_odds

    @property
    def formatted_odds(self):
        result = copy.deepcopy(self.raw_odds)
        if result is not None:
            for idx in range(len(result)):
                for idy in range(len(result[idx])):
                    if result[idx][idy] is not None:
                        if idx % 3 == 0 and idy % 3 == 1:
                            # Get Goal 2 ZH
                            if result[idx][idy] > 10 or result[idx][idy] < -10:
                                result[idx][idy] = str(result[idx][idy]) + u"\u7403"
                            else:
                                _ret1 = "" if result[idx][idy] >= 0 else u"\u53D7"
                                _ret2 = GOAL_ZH_HK.split(",")[abs(int(result[idx][idy] * 4))]
                                result[idx][idy] = _ret1 + _ret2
                        else:
                            # Format to Two Decimal
                            result[idx][idy] = str("{0:.2f}".format(result[idx][idy]))
                    else:
                        result[idx][idy] = ""
        return result

    @property
    def asian_odds_diff_from_initial(self):
        __idx__ = 0
        if self.raw_odds is None:
            return None
        else:
            if self.raw_odds[__idx__][1] is not None and self.raw_odds[__idx__][4] is not None:
                return self.raw_odds[__idx__][1] != self.raw_odds[__idx__][4]
            else:
                return False

    @property
    def ls_odds_diff_from_initial(self):
        __idx__ = 2
        if self.raw_odds is None:
            return None
        else:
            if self.raw_odds[__idx__][1] is not None and self.raw_odds[__idx__][4] is not None:
                return self.raw_odds[__idx__][1] != self.raw_odds[__idx__][4]
            else:
                return False

    @property
    def all_attributes(self):
        result = dict(vars(self), asian_odds=self.asian_odds_diff_from_initial, ls_odds=self.ls_odds_diff_from_initial,
                      odds=self.formatted_odds, status=self.status_text)
        result.pop("raw_odds")
        return result
