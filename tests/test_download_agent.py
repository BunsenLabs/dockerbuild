from dockerbuild.download_agent import DownloadAgent

def test_canary_download(tmp_path, opts_nobody_uid_gid):
        agent = DownloadAgent(opts_nobody_uid_gid)
        tmp_path.chmod(0o777)
        dest = tmp_path / "destination.tar.gz"
        result = agent.download("https://github.com/BunsenLabs/bunsen-os-release/archive/10.4.0-1.tar.gz", dest)
        assert result == True
        #return result == True and dest.is_file() and dest.stat().st_size != 0
