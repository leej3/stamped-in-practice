"""Exact shared copy/hash primitives extracted from reviewed judge preserver."""
from pathlib import Path
import hashlib,importlib.util,os,stat,sys
sys.dont_write_bytecode=True
HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location('frozen_capture',HERE/'frozen_delivery_snapshot.py');F=importlib.util.module_from_spec(spec);spec.loader.exec_module(F)
sha=lambda data:hashlib.sha256(data).hexdigest()
omissions=[]
errors=[]
def scan(source,destination=None):
    rows=[]
    def visit(parent,name,relative,physical,dest):
        before=os.stat(name,dir_fd=parent,follow_symlinks=False)
        row={'path':relative,'mode':stat.S_IMODE(before.st_mode),'source_signature':list(F._signature(before))}
        if F._credential_path(physical):
            row.update(kind='omitted-credential');omissions.append({'source':str(physical),'reason':'Frozen capture known-credential exclusion'});rows.append(row);return
        if stat.S_ISDIR(before.st_mode):
            fd=os.open(name,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW,dir_fd=parent)
            try:
                assert F._signature(before)==F._signature(os.fstat(fd)),str(physical)
                row['kind']='directory';rows.append(row)
                if dest is not None:dest.mkdir()
                for child in sorted(os.listdir(fd)):
                    visit(fd,child,child if relative=='.' else relative+'/'+child,physical/child,dest/child if dest is not None else None)
                assert F._signature(before)==F._signature(os.fstat(fd)),str(physical)
                if dest is not None:os.chmod(dest,row['mode'])
            finally:os.close(fd)
        elif stat.S_ISREG(before.st_mode):
            digest=F._read_file(parent,name,before,dest)
            row.update(kind='file',size=before.st_size,sha256=digest);rows.append(row)
            if dest is not None:os.chmod(dest,row['mode'])
        elif stat.S_ISLNK(before.st_mode):
            link=os.readlink(name,dir_fd=parent);row.update(kind='symlink',link_target=link,sha256=sha(os.fsencode(link)));rows.append(row)
            assert F._signature(before)==F._signature(os.stat(name,dir_fd=parent,follow_symlinks=False)),str(physical)
            if dest is not None:
                os.symlink(link,dest)
                if hasattr(os,'lchmod'):os.lchmod(dest,row['mode'])
        else:
            row.update(kind='unsupported');rows.append(row);errors.append({'source':str(physical),'reason':'Unsupported special file retained only as metadata'})
    descriptor=os.open(source.parent,os.O_RDONLY|os.O_DIRECTORY|os.O_NOFOLLOW)
    try:visit(descriptor,source.name,'.',source,destination)
    finally:os.close(descriptor)
    return rows

def content_index(rows):return [{k:v for k,v in row.items() if k!='source_signature'} for row in rows]
