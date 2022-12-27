import iksm
import json
import os, re, sys

def sign_in():
  # 認証用のURL取得
  oauthURL = iksm.get_session_token_code()
  print("Navigate to this URL in your browser:")
  print(oauthURL)
  print("Log in, right click the \"Select this account\" button, copy the link address, and paste it below:")
  while True:
    try:
      url_scheme = input("")
      iksm.get_cookie(url_scheme)
      break
    except KeyboardInterrupt:
      sys.exit(1)
    except AttributeError:
      pass
    except KeyError:
      pass

if __name__=='__main__':
  try:
    summary = iksm.get_coop_summary()
  except FileNotFoundError:
    sign_in()
