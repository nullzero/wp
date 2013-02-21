/*
TASK: oct27_rle2
LANG: C++
AUTHOR: Sorawee Porncharoenwase
*/

// Prob. statement: http://theory.cpe.ku.ac.th/~pramook/ioi/2011/oct27_rle2.pdf

#include <iostream>
#include <string>
#include <vector>
#include <algorithm>

using namespace std;

const int N(701);

struct Unicode{
    string ch;
    
    bool operator==(const Unicode& o)const{
        return ch == o.ch;
    }
    
    Unicode(string _ch){
        ch = _ch;
    }
};

vector<Unicode> str;

int A[N][N], O[N][N];
bool sp[N][N], sm[N][N];

inline bool match(int a, int b, int c){
    while(a <= b){
        if(str[a] == str[c]){
            a++;
            c++;
        }else{
            return false;
        }
    }
    return true;
}

int cp(int l, int r){
    if(l == r) return 1;
    if(sp[l][r]) return A[l][r];
    sp[l][r] = true;
    int lim = (l + r) >> 1;
    for(int i = r - 1; i >= lim; --i){
        if((i - l + 1) % (r - i) != 0) continue;
        int now = cp(l, i);
        if(i - l + 1 == now * (r - i) and match(i + 1, r, l)){
            A[l][r] = now + 1;
            return A[l][r];
        }
    }
    return A[l][r] = 1;
}

inline int f(int a){
    int ans = 0;
    while(a > 0){
        ++ans;
        a /= 10;
    }
    return ans;
}

int cm(int l,int r){
    if(l == r) return 1;
    if(sm[l][r]) return O[l][r];
    sm[l][r] = true;
    int vmin = r - l + 1;
    for(int i = l; i < r; ++i){
        int now = cm(l, i) + cm(i + 1, r);
        if(now < vmin) vmin = now;
    }
    int ll = cp(l, r);
    if(ll != 1){
        int alt = f(ll) + ((r - l + 1 == ll) ? 1 : 2 + cm(l, l - 1 + (r - l + 1) / ll));
        if(vmin > alt) vmin = alt;
    }
    return O[l][r] = vmin;
}

int main(){
    string s;
    while(getline(cin, s)) str.push_back(Unicode(s));
    int len = min((int)str.size(), 700);
    cout << len - cm(0, len - 1);
    return 0;
}

/*
a
b
b
b
b
b
a
a
b
b
b
b
b
a
*/
