## Apple Store Application

> Django로 구현한 애플스토어 어플리케이션

## 프로젝트 구조 설명

**core**

    - 환경 설정(settings.py)
    - 메인 URL 주소(urls.py)

**eccomerce**

    - 메인 프로젝트 디렉토리
    - 모델 설정(models.py)
    - 어드민 설정(admin.py)
    - api
        - views
            - API를 구현한 비즈니스 로직
        - serializers.py
            - 모델 인스턴스를 JSON 형태로 렌더링
        - urls.py
            - API 주소

## 환경 설정 구조 설명

**1) 설치한 라이브러리**

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'django.contrib.sites',
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'corsheaders',
    'rest_auth',
    'rest_auth.registration',
    'rest_framework',
    'rest_framework.authtoken',

    'crispy_forms',
    'django_countries',

    'ecommerce',
]
```

- corsheaders
  다른 도메인에 있는 프론트엔드 쪽에서 서버의 리소스를 액세스 할 수 있도록 CORS 추가

- rest_framework
  Django에서 REST API 서비스를 구현하기 위해 앱 추가

- rest_auth
  토큰 기반 사용자 인증을 구현하기 위해 앱 추가

- django_countries
  배송지 주소 선택시 Form에서 국가 선택지를 제공받기 위해 앱 추가

**2) CORS Whitelist**

- 프론트엔드가 가진 도메인 주소를 승인

```python
CORS_ORIGIN_WHITELIST = (
    'http://localhost:3000',
)
```

**3) Permission and Authentication**

```python
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.AllowAny',
    ),
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
    ),
}
```

- 기본값으로 Permission은 AllowAny로 모든 사용자에게 허용
- 사용자 인증의 기본값으로 TokenAuthentication(토큰 기반 인증을 사용)

## 모델 구조 설명

**사용자(User)**

    - Django에서 제공해주는 AUTH_USER_MODEL 사용

**사용자 프로필(User Profile)**

    - Django Signals를 사용하여 사용자 생성시 자동생성

```python
def userprofile_receiver(sender, instance, created, *args, **kwargs):
    if created:
        userprofile = UserProfile.objects.create(user=instance)
post_save.connect(userprofile_receiver, sender=settings.AUTH_USER_MODEL
```

**상품(Item)**

    - 개시되어 있는 개별적인 상품들

**상품 옵션(Option)**

    - 상품이 가진 옵션이며 이름을 가짐

**상세 옵션(Option Value)**

    - 상품 옵션이 가진 값

**주문 상품(Order Item)**

    - 사용자가 장바구니에 추가한 상품

**주문(Order)**

- 사용자의 장바구니를 의미하며, 첫 상품 추가한 시점부터 생성

```python
user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
items = models.ManyToManyField('OrderItem')
start_date = models.DateTimeField(auto_now_add=True)
ordered_date = models.DateTimeField()
ordered = models.BooleanField(default=False)

shipping_address = models.ForeignKey(
    'Address', on_delete=models.SET_NULL, related_name='shipping_address', blank=True, null=True)
billing_address = models.ForeignKey(
    'Address', on_delete=models.SET_NULL, related_name='billing_address', blank=True, null=True)

payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, blank=True, null=True)
coupon = models.ForeignKey('Coupon', on_delete=models.SET_NULL, blank=True, null=True)

ref_code = models.CharField(max_length=30)

being_delivered = models.BooleanField(default=False)
received = models.BooleanField(default=False)
refund_requested = models.BooleanField(default=False)
refund_granted = models.BooleanField(default=False)
```

**배송지 주소 & 청구지 주소(Address)**

**결제(Payment)**

    - 결제 방법: Stripe Online Payment

**할인권(Coupon)**

**환불(Refund)**

## 뷰 구조 설명

**views.py**

    - 예외적인 API들의 모듈
    - UserIDView: 사용자 아이디 GET 방식 API
    - AddCouponView: 쿠폰 입력 POST 방식 API
    - CountryListView: 국가 리스트 GET 방식 API

**products.py**

    - 상품 관련 API들의 모듈
    - ItemListView: 상품 리스트 GET 방식 API
    - ItemDetailView: 상세 상품 GET 방식 API
    - AddToCartView: 상품 장바구니 추가 POST 방식 API
    - SubtractItemQuantityView: 상품 개수 차감 POST 방식 API

**orders.py**

    - 상품 주문 관련 API들의 모듈
    - OrderDetailView: 사용자의 장바구니 현황 GET 방식 API
    - OrderItemDeleteView: 장바구니에 상품 삭제 DELETE 방식 API

**addresses.py**

    - 주소 관련 API들의 모듈
    - AddressListView: 사용자의 배송지 주소 와 청구지 주소 GET 방식 API
    - AddressCreateView: 새로운 주소 POST 방식 API
    - AddressUpdateView: 기존의 주소 PUT 방식 API
    - AddressDeleteView: 기존의 주소 DELETE 방식 API

**payments.py**

    - 결제 관련 API들의 모듈
    - PaymentView: 결제 정보 POST 방식 API
    - PaymentListView: 결제 내역 GET 방식 API
