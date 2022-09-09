import iksm
import os, re, sys


if __name__=='__main__':
  summary = iksm.get_coop_summary()
  print(summary)
  # # 認証用のURL取得
  # oauthURL = iksm.get_session_token_code()
  # print("Navigate to this URL in your browser:")
  # print(oauthURL)
  # print("Log in, right click the \"Select this account\" button, copy the link address, and paste it below:")
  # while True:
  #   try:
  #     url_scheme = input("")
  #     iksm.get_cookie(url_scheme)
  #   except KeyboardInterrupt:
  #     sys.exit(1)
  #   except AttributeError:
  #     pass
  #   except KeyError:
  #     pass
