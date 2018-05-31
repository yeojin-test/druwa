"""
패스트캠퍼스 WPS 8기 크롤링 과제
네이버 웹툰 크롤링하기

만든사람: 김여진
만든날짜: 2018.5.30
License: MIT(or 500won)

+ 만약 모듈로 쓴다면 Manager 클래스만 사용하자
+ ex) from NaverWebtoonCrawler import Manager

(1)
+ html 뷰어는... 더이상은 naver
+ 만들고 싶다면
+ html 생성 라이브러리 : ElementTree (https://wikidocs.net/42)
+ 웹브라우저 컨트롤 라이브러리 : webbrowser (https://docs.python.org/3.6/library/webbrowser.html)
(2)
+ 피드백과 주석 정리 후 본 포폴용 계정에 올리기
+ 패키지로 분리할지를 고려(연습용)
+ 최적화...는 잘 모르겠음 - 웹툰 번호의 경우 int 연산이면 더 좋지 않을까?
"""

import os
import re
from urllib import parse

import requests
from bs4 import BeautifulSoup

# Manager 클래스로 다 동작하도록 구현해놓았음
__all__ = ['Manager']

"""
1. 동작하는 클래스 : CrawlerAgent, Manager
"""


class CrawlerAgent:
    """
    크롤러 에이전트 - 크롤링을 해준다
    """

    def __init__(self):
        """ 크롤러 에이전트는 스태틱 메소드만 있다. """
        pass

    @staticmethod
    def crawl(path, url, param=None):
        """
        크롤링 메소드(BeautifulSoup, Requests 라이브러리 필요)
        :parameter
        path: 데이터 저장 경로
        url: request uri
        param: get url을 만들기 위한 쿼리

        :return
        BeautifulSoup 인스턴스
        """

        # 입출력, 인터넷 연결 부분은 예외처리
        try:
            # 디렉토리가 없을 경우 생성해준다(그냥은 안만들어줌)
            if not os.path.exists(os.path.dirname(path)):
                os.makedirs(os.path.dirname(path))

            # 파일이 존재할 경우 읽고 없으면 새로 쓰지는 않는다
            # issue: 한번 받으면 그 후로는 네이버 사이트에서 다운로드하지 않음
            if not os.path.exists(path):
                response = requests.get(url, params=param)
                with open(path, 'xt', encoding='UTF-8') as f:
                    f.write(response.text)
            html = open(path, 'rt', encoding='UTF-8').read()

            soup = BeautifulSoup(html, 'lxml')
            return soup
        except ConnectionError as e:
            print('인터넷에 연결되지 않았습니다')
            print(e)
        except IOError as e:
            print('파일 생성에 문제가 있습니다.')
            print(e)


class Manager:
    """
    웹툰 관리자 - 크롤링 전반적인 기능을 가지고 있다
    issue: singleton?
    """

    # 네이버 웹툰 get url을 만들기 위한 base url
    webtoon_base_url = 'http://comic.naver.com/webtoon/list.nhn?'

    # 네이버 웹툰 에피소드 get url을 만들기 위한 base url
    episode_base_url = 'http://comic.naver.com/webtoon/detail.nhn?'

    # 네이버 웹툰 전체 데이터를 담은 딕셔너리(key-타이틀, value-고유번호)
    webtoon_dict = dict()

    # webtoon_dict에 검색어에 해당하는 웹툰이 있는지 검색 후 결과 리스트 리턴
    @classmethod
    def search(cls, query):
        """
        검색어에 따라서 네이버 웹툰을 검색해준다
        :param query: 웹툰번호(숫자/문자열), 웹툰 이름(문자열)
        :return result: 결과 리스트
        """

        # 숫자(웹툰번호)도 문자열으로
        query = str(query) if isinstance(query, int) else query

        # webtoon.dict()가 없다면 만들어준다
        if not cls.webtoon_dict:
            print('웹툰 정보를 업데이트합니다.')
            Manager.update()

        # return을 위한 result 리스트, 항목은 딕셔너리
        result = list()

        # 웹툰 이름이든 웹툰 번호든 알아서 찾아줌
        # 그래서 느릴 것 같다 -> webtoon_dict 구조를 수정하는 것은 너무 큰 작업 -> 계획을 잘 세우자
        for title, titleId in cls.webtoon_dict.items():
            # 웹툰 이름은 부분검색, 웹툰 번호는 전체일치
            if query in title or query == titleId:
                result_item = {
                    'title': title,
                    'titleId': titleId
                }
                result.append(result_item)

        return result

    @classmethod
    def make_webtoon(cls, query, with_episode=False):
        """
        웹툰 인스턴스를 만들어준다.
        :param query: 그냥 search() 메소드에서 결과를 받아온다
        :param with_episode: with_episode=True이면 episode_list도 다운로드, False이면 빈 리스트(양심상...)
        :return: 웹툰 인스턴스 리턴
        """

        # query에 대한 결과 받아오기(여러개일 수 있어서 첫번째만 -> 딕셔너리 타입)
        result = cls.search(query)
        if len(result) == 0:
            print('해당 웹툰이 없습니다. 웹툰 번호나 이름을 확인하세요.')
            return
        else:
            result = result[0]

        title = result['title']
        webtoon_id = result['titleId']

        # 웹툰의 기본 정보(info.html에 담긴다)의 경로 설정, 혹시 몰라서 공백 제거
        # info.html은 첫 번째 화면(웹툰 리스트 1페이지)
        # 여러 페이지를 받아올 수도 있겠지만... naver
        webtoon_path = f"naver_webtoon_data/webtoon_{title.replace(' ', '_')}/info.html"

        # 웹툰 번호만으로 접근 가능, 요일은 필요없다
        param = {'titleId': webtoon_id}

        # 크롤링
        soup = CrawlerAgent.crawl(webtoon_path, cls.webtoon_base_url, param)

        # 지난 시간 코드 재활용
        detail = soup.select_one('div.detail > h2')

        # 요일 정보를 추가해야만 한다면 여기에!
        info = dict()
        info['title'] = detail.contents[0].strip()
        info['author'] = detail.span.get_text(strip=True)
        info['description'] = soup.select_one('div.detail > p').get_text()

        # with_episode 플래그에 따라 episode_list 크롤링
        if with_episode:
            episode_info_list = soup.select('table.viewList > tr')

            episode_list = list()

            for episode_info in episode_info_list:
                # class가 달려있는 tr 태그는 쓸모없다(등록일자가 있는 태그)
                if episode_info.get('class'):
                    continue

                episode_dict = dict()

                # urlib 라이브러리를 통해 썸네일 url 속 에피소드 번호를 파싱
                # 그냥 정규표현식이 편할 것 같다. 한다면 'no=(\d+)'
                episode_dict['no'] = \
                    parse.parse_qs(parse.urlsplit(episode_info.select_one('td:nth-of-type(1) a').get('href'))
                                   .query)['no'][0]
                episode_dict['url_thumbnail'] = episode_info.select_one('td:nth-of-type(1) img').get('src')
                episode_dict['title'] = episode_info.select_one('td:nth-of-type(2) a').get_text()
                episode_dict['rating'] = episode_info.select_one('td:nth-of-type(3) strong').get_text()
                episode_dict['created_date'] = episode_info.select_one('td:nth-of-type(4)').get_text()

                episode_element = Episode(webtoon_id, episode_dict)
                episode_list.append(episode_element)

            info['episode_list'] = episode_list

        else:
            info['episode_list'] = list()

        return Webtoon(webtoon_id, info)

    @classmethod
    def update_webtoon(cls, webtoon):
        """
        episode_list가 빈 리스트인 웹툰 인스턴스에 episode_list 생성
        생성이라고 썼지만 그냥 make_webtoon() 다시 돌린다 ㅋㅋ
        :param webtoon:
        :return:
        """
        if isinstance(webtoon, Webtoon):
            return cls.make_webtoon(webtoon.webtoon_id, True)
        else:
            print('Webtoon 인스턴스가 아닙니다.')
            return

    @classmethod
    def download_episode(cls, webtoon, min_no=1, max_no=1, all_epi=False):
        """
        에피소드 다운로드 메소드(철컹철컹)
        :param webtoon:
        :param min_no: 다운로드 시작 에피소드 번호, 기본값은 1(첫번째 에피소드)
        :param max_no: 다운로드 끝 에피소드 번호, 기본값은 1(첫번째 에피소드)
        :param all_epi: True일 경우 모든 에피소드를 받아온다!(궁극기)
        :return: naver_webtoon_data 디렉토리 아래에 다운로드가 되어있다
        """
        if not isinstance(webtoon, Webtoon):
            print('Webtoon 인스턴스가 아닙니다')
            return

        # episode_list가 빈 리스트일 경우
        if len(webtoon.episode_list) == 0:
            print('웹툰의 에피소드 리스트 정보가 없습니다.\nupdate_webtoon() 메소드를 사용하세요')
            return
        else:
            # 현재 최신화 에피소드 번호
            max_num = int(webtoon.episode_list[0].no)

        # min_no, max_no check!
        if max_no > max_num or min_no < 1 or min_no > max_no:
            print('웹툰 번호가 잘못되었습니다.')
            return

        # all 플래그가 True이면 전부 다 받을 수 있도록 범위 설정
        if all_epi:
            max_no = max_num
            min_no = 1

        # 이미지 다운로드
        # CrawlerAgent로 처리하면 더 느려질 것 같아 직접 구현
        for no in range(min_no, max_no + 1):
            episode_dir = f"naver_webtoon_data/webtoon_{webtoon.title.replace(' ', '_')}/{str(no)}/"
            param = {'titleId': webtoon.webtoon_id, 'no': str(no)}

            soup = CrawlerAgent.crawl(episode_dir + 'episode_info.html', cls.episode_base_url, param)
            imgs = soup.select('div.wt_viewer > img')

            # 403 메세지를 피하기 위한 header(핵심기술)
            header = {'Referer': cls.episode_base_url + parse.urlencode(param)}

            # 입출력, 인터넷 연결 부분은 예외처리
            try:
                # 이미지 다운로드 -> 그냥 바이너리로 쓴다(가희님 도움)
                for img in imgs:
                    # 이미지 파일명은 img 태그의 id 사용
                    image_file_path = episode_dir + img['id'] + '.jpg'
                    image_file_data = requests.get(img['src'], headers=header, params=param).content
                    # episode_info.html 파일을 만들면서 디렉토리는 생성되었기 때문에 바로 파일 생성
                    open(image_file_path, 'wb').write(image_file_data)
            except ConnectionError as e:
                print('인터넷에 연결되지 않았습니다.')
                print(e)
            except IOError as e:
                print('파일 생성에 문제가 있습니다.')
                print(e)

    @classmethod
    def update(cls):
        """
        webtoon_dict를 최신화
        :return: webtoon_dict 딕셔너리
        """

        # 웹툰 번호를 뽑아내기 위한 정규표현식
        extract_id = re.compile('webtoon/(\d+)')

        # 네이버 웹툰 메인페이지 주소
        home_url = 'http://comic.naver.com/webtoon/weekday.nhn'
        webtoon_list_path = f'naver_webtoon_data/webtoon_list.html'

        webtoon_dict = dict()

        # 웹툰 메인페이지에서 웹툰 이름과 웹툰 번호 크롤링 후 webtoon_dict에 저장
        soup = CrawlerAgent.crawl(webtoon_list_path, home_url)
        # 1번째 img 태그만 사용한다. 2번째는 아이콘이 있을 수 있음
        imgs = soup.select('div.thumb > a > img:nth-of-type(1)')

        for img in imgs:
            title = img['title']
            # 정규표현식으로 웹툰 번호 추출
            webtoon_id = re.search(extract_id, img['src']).group(1)
            # webtoon_dict에 title, webtoon_id 추가
            webtoon_dict[title] = webtoon_id

        cls.webtoon_dict = webtoon_dict

        # webtoon_dict 리턴(전체 웹툰 리스트를 보려면 사용)
        return webtoon_dict


"""
2. 정보 구조를 갖는 클래스 : Webtoon, Episode
issue: EpisodeImage에 대한 리스트 
"""


class Webtoon:
    """
    네이버 웹툰 정보 클래스
    전체 웹툰 리스트는 Manager.update() 사용
    """

    def __init__(self, webtoon_id, info):

        # 웹툰 고유 ID, 6자리 숫자이나 문자열 처리(super key)
        self.webtoon_id = webtoon_id

        # info 딕셔너리에서 만드는 Webtoon 클래스의 인스턴스 변수들(key)
        #   title: 웹툰 이름
        #   author: 웹툰 저자
        #   desciption: 웹툰 설명
        #   episode_list: 웹툰 에피소드(Episode 클래스) 리스트
        # 아래 코드가 간단하지만 툴팁에 반영이 안되는 문제가 있음
        vars(self).update(info)


class Episode:
    """
    웹툰 에피소드 정보 클래스
    에피소드 전체 정보는 웹툰 인스턴스의 episode_list 참
    """

    def __init__(self, webtoon_id, info):

        # make_webtoon 클래스의 episode_info 딕셔너리를 넘겨받아 초기화(with_episode 플래그 참고)
        # 에피소드의 웹툰 고유 ID, 에피소드가 어떤 웹툰의 에피소드인지 알 수 있다
        self.webtoon_id = webtoon_id

        # info 딕셔너리에서 만드는 Webtoon 클래스의 인스턴스 변수들(key)
        #   no: 에피소드 번호(super key)
        #   url_thumbnail: 썸네일 이미지 url
        #   title: 에피소드 이름
        #   rating: 별점
        #   created_date: 게시일
        # 아래 코드가 간단하지만 툴팁에 반영이 안되는 문제가 있음
        vars(self).update(info)

    # 에피소드로 이동하는 url 주소
    @property
    def url(self):
        data = {
            'titleId': self.webtoon_id,
            'no': self.no
        }
        return Manager.webtoon_base_url + parse.urlencode(data)


'''
Test Codes
'''
if __name__ == '__main__':
    # '유미'라는 검색어로 웹툰 검색, '암행'이라는 검색어로 웹툰 검색
    print('---test1---')
    print(Manager.search('유미'))
    print(Manager.search('암행'))
    print('\n\n')

    # '평범한 8반'이라는 검색어로 웹툰 검색하고 첫 번째 결과에 대한 Webtoon 인스턴스 생성
    print('---test2---')
    ban8 = Manager.make_webtoon(Manager.search('평범한 8반')[0]['title'], with_episode=True)
    print(ban8)
    print('\n\n')

    # 웹툰 번호를 직접 넣어도 인스턴스 생성
    print('---test3---')
    print(703845, Manager.make_webtoon(703845, with_episode=True).title)
    print('\n\n')

    # 웹툰 이름을 직접 넣어도 인스턴스 생성
    print('---test4---')
    죽음에_관하여 = Manager.make_webtoon('죽음에 관하여 (재)', with_episode=True)
    print(죽음에_관하여.title)
    print('\n\n')

    # ban8 인스턴스의 에피소드 제목과 에피소드 번호, 별점 출력
    print('---test5---')
    for episode in ban8.episode_list:
        print(episode.title, episode.no, episode.rating)
    print('\n\n')

    # ban8 인스턴스(웹툰)의 3~8번 에피소드 이미지 크롤링
    print('---test6---')
    Manager.download_episode(ban8, 3, 8)
    print('\n\n')

    # 죽음에_관하여 웹툰의 모든 에피소드 크롤링
    # 경고 : 매우 느림
    # print('---test7---')
    # Manager.download_episode(죽음에_관하여, all_epi=True)
